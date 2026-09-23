# Vetting record: `RL34`

#### Vetted 2026-09-23, before any citation from it entered the manuscript.
#### Procedure: `README.md` section *Vetting a returned report, BEFORE any value enters a document* (7 steps).
#### Prompt: `L34_equation_sources.md`. Response: `RL34_equation_sources.md` (43,474 B, returned 2026-09-23).
#### Provenance reference: `TRANSCRIPT_NOTES_RL34_RL35_RL36.md` (what the external session actually downloaded).
#### External calls made by this vetting: Crossref `api.crossref.org/works/<DOI>` for 23 DOIs, DataCite `api.datacite.org/dois/<DOI>` for 2 arXiv DOIs. Nothing else online.

---

## VERDICT

| Part of `RL34` | Verdict | Carried | Rejected |
|---|---|---|---|
| **Bibliographic identity (DOIs)** | **MOSTLY HOLDS.** 21 of 21 recommended Crossref DOIs resolve, and the negative control is a real 404. Title, first author, year and venue match on all 21 except one: Carlini et al. (2022), where the **pages** and **one author name** are wrong. The DataCite record for Borisov et al. has a **different author list** from the one the report prints. | The DOI strings, with the Crossref fields below | Carlini pages `2653-2670` and author "Nasraheny"; Borisov author list; the 2nd-edition ISBN for Levin, Peres and Wilmer (check digit invalid) |
| **Opened / inferred split** | **FAILED.** The report claims **25** documents "opened in full". The transcript supports **11**. The other **14**, including Deming and Stephan, Deville and Sarndal, Beckman, Willmott, Yeom, Carlini, Hanley, Lowe, Borisov and both TABULA documents, were never downloaded. | Nothing from the "Text Opened" column | Every page, section, table or equation pointer into a document the transcript does not show opened |
| **Eq. 13, Jordan and Vajen Table 1** | **HOLDS, checked against our own PDF.** All 30 values of Table 1 match our local copy exactly, and Table 1 is on PDF page 5 as stated. | Table 1 values; "Table 1, p. 5" | The unit "L/min" added to sigma (the source prints none) and the description of how our code uses sigma |
| **Eq. 12, CREST side-by-side** | **FAILED as a quotation of Richardson et al. (2010).** The CREST formula shown is our own code's docstring, relabelled as `richardsonpy`. Our half matches our code's closed form, but two statements about our code are wrong and the production calibration loop is missed entirely. | Richardson et al. (2010), Section 2.7, as the place to look | The displayed CREST formula as "Richardson et al. (2010)"; "guaranteeing non-negative"; the explanation of CREST's failure mode |
| **Statements about our prompt** | **FAILED.** The report "corrects" two errors that the prompt never made (a Beckman DOI and a JASSS venue for Lovelace and Ballas). | none | both "corrections" |
| **Classifications (STANDARD / ADAPTED / OWN)** | **ACCEPTED, with low value.** The three OWN verdicts (transfer margin, fictional-country steering, gain redistribution) are exactly the guesses the prompt supplied. | the three OWN verdicts, stated in the first person as our own search | none |
| **Pushbacks against the prompt's own suggestions** | **The round's real product.** Shokri is not the source for a loss-threshold attack; Lovelace and Ballas do not describe plain largest remainder; Park et al. may not define NNDR. All three move against the prompt, none in a rescuing direction. | all three, as leads for the author to confirm | none |

**Overall: PARTLY ACCEPTED as a citation map.** 14 citations may enter the manuscript now, 14 only after the author opens them, 1 is rejected. **No DOI is fabricated.** One citation carries wrong pages and an invented author name, one carries a wrong author list, one ISBN is invalid, and 14 "full text" claims are unsupported by the transcript.

---

## 1. Checks run, and what each returned

### 1.1 Positive and negative controls (Crossref, re-run by us)

| Control | Report says | Crossref today | State |
|---|---|---|---|
| `10.1016/j.enbuild.2010.05.023` | Richardson, *Domestic electricity use: A high-resolution energy demand model*, Energy and Buildings 42(10) 1878-1887, 2010 | same, all fields | **HOLDS** |
| `10.1016/j.enbuild.2099.00001` | 404 NOT FOUND | 404 `Resource not found.` | **HOLDS** |

The search was not broken, and the made-up DOI did not come back with a record.

### 1.2 The opened / inferred split against the transcript (README step 3)

`RL34` Mandatory Question 1 lists **25** documents "opened in full". `TRANSCRIPT_NOTES_RL34_RL35_RL36.md` lists what was actually downloaded and text-searched.

| Claimed "opened in full" | Supported by transcript? |
|---|---|
| Lovelace and Ballas 2013 (arXiv 1303.5228) | **yes** |
| Hyndman and Koehler 2006 (preprint `mase.pdf`) | **yes**, but the preprint, so journal page numbers (p. 682, pp. 683-684) cannot come from it |
| Levin, Peres and Wilmer (uoregon PDF) | **yes, first 100 pages only** |
| Lin 1991 (course-site copy) | **yes** |
| Richardson et al. 2008 (Loughborough figshare) | **yes** |
| Richardson et al. 2010 (Loughborough figshare), section "2.7 Appliance calibration scalars" | **yes** |
| Park et al. 2018 (vldb.org PDF) | **yes**, but the result of the `'NNDR' in text` test is not shown |
| Platzer and Reutterer 2021 (Frontiers PDF) | **yes** |
| Jordan and Vajen 2001a | **yes, but it is OUR OWN local copy** read from our repo |
| Hu et al. LoRA (arXiv PDF) | **yes, first 10 pages** |
| Ramdas, Garcia Trillos and Cuturi (arXiv 1509.02237) | **yes** (the Entropy PDF fetch is not shown to succeed) |
| Deming and Stephan 1940 | **no** |
| Deville and Sarndal 1992 | **no** |
| Beckman, Baggerly and McKay 1996 | **no** |
| Willmott and Matsuura 2005 | **no** |
| Montgomery, Peck and Vining 2012 | **no** |
| Vallender 1974 | **no** (metadata only) |
| Villani 2003 | **no** |
| Yeom et al. 2018 | **no** (metadata only) |
| Carlini et al. 2022 | **no** |
| Hanley and McNeil 1982 | **no** (metadata only) |
| Lowe 2004 | **no** |
| Loga, Diefenbach and Stein 2012 (TABULA Synthesis Report) | **no**; only our repo's `archetype_parameter_provenance.md` was read |
| Loga, Stein and Diefenbach 2016 | **no** |
| Borisov et al. 2023 | **no** |

**11 of 25 supported, 14 not.** Every one of the 14 carries an exact page, section, theorem or table pointer in Section B (for example Deming "pp. 439-444, Section 3", Willmott "p. 79, Eq. (1)", Carlini "pp. 2655-2658", TABULA "p. 25, Table 7"). **Those pointers cannot have been read, so none of them may be printed.** The same failure was recorded for `RL30`/`RL31`.

Section F "Confirmed reachable?" is no better. The two md5 values given as "verified on disk" (`c7c460...` for Jordan and Vajen, `c99ddc...` for the TABULA calculator) are **the md5s of our own files**, already recorded in our repo (`Step9_docs/.../sources/`, `Step8_docs/outputs_step8/archetype_parameter_provenance.md`, line 26). They show the session read our disk. They say nothing about the URLs. The TABULA Synthesis Report row says "Yes" with no download in the transcript.

### 1.3 Statements about our prompt that are false (README step 1)

| Report says | Our prompt `L34` actually says | State |
|---|---|---|
| "The printed DOI in prompt L34 is a typographical error (ends in 00003-6 which 404s)" (Section C, Section G) | Beckman et al. is given as "Transportation Research A 30(6) 415-429" with **no DOI at all** | **FALSE.** Our manuscript already carries the correct `10.1016/0965-8564(96)00004-3` (`writing/submission/4J_manuscript_submission.md`, line 1377). `00003-6` appears nowhere in our repo outside `RL34`. The "Design change: correct DOI" fixes an error nobody made. |
| "The prompt suggested Lovelace and Ballas (2013) was in JASSS" (Section G) | "for example Lovelace and Ballas 2013 on integerisation, 'truncate, replicate, sample'; verify" (no venue). JASSS is given for Lovelace **et al. (2015)** | **FALSE.** Invented, then corrected. |

(We confirm independently that `10.1016/0965-8564(96)00003-6` is a Crossref 404, so the report did query it; it simply attributed a DOI it made up to us.)

### 1.4 Eq. 12: does Richardson et al. (2010) give the CREST calibration, and does the side-by-side match our code? (check a)

**What the report shows as CREST's equation** (Part 2):

```
lambda = C / (Y * P_occupied - t_running - C * D)
hazard_CREST = lambda / P_activity_bar
```

attributed to "the open reference implementation (`richardsonpy/classes/appliance.py`)". **The transcript shows no fetch of `richardsonpy`.** The formula is our own docstring, `tools/4thJ_step9_trigger.py` lines 341-342:

```
CREST:      lambda = cycles / (year_minutes*p_occ - t_running - cycles*delay)
            hazard = lambda / mean_activity_probability
```

and our module header (line 10) names `richardsonpy/classes/appliance.py` as the source of the state machine. The prompt also printed the same formula. **So the CREST half of the side-by-side is our text handed back.** It is not evidence of what Richardson et al. (2010) prints. The report itself concedes the paper has "no numbered display equation", which leaves the question the prompt asked (the exact printed equation and its number) **unanswered**.

**Our half** matches the closed form in `calibrate()` (lines 338-369): `unavailable = C*(L+D)`, `available = E - unavailable*(E/525600)`, `h = C/available`. That part is right, and it is a restatement of our code and prompt (README step 2: worth nothing).

**What the report gets wrong about our code:**

| Report says | Our code | State |
|---|---|---|
| Eq. 12 "guarantee[s] that available minutes remain well-scaled and non-negative whenever the appliance physically fits within the eligible activity window" | `available = E * (1 - C*(L+D)/525600)`. It is positive only when `C*(L+D) < 525,600`, that is when the appliance's busy time fits inside **the year**, independent of `E`. When it is not positive the code **raises `TriggerError`** (line 357), and it also raises when `h >= 1` (line 364). Nothing is guaranteed. | **WRONG** |
| CREST's form "can cause mathematical anomalies or negative hazards if activity probability is low" | Dividing by a small activity probability makes the hazard **large** (possibly above 1), not negative. A negative value can only come from the denominator `Y*P_occ - t_running - C*D`. | **WRONG** (mis-statement of CREST) |
| Eq. 12 "operates directly on individual synthetic diaries rather than population-level product probabilities" | Eligibility is per diary minute (`day_profile_index`, active occupant only, line 218). But the hazard is **one stock-level value per appliance**, from the stock mean eligible minutes (`calibrate_all`, line 675: `calibrate(app, elig * 1.0, 1)`). | **half right** |
| (not mentioned) | **Production runs do not stop at the closed form.** `run_fold` calls `calibrate_to_published` by default (`calibration_passes=6`, tolerance 2 %, lines 804-872), which rescales each hazard until the stock mean cycles per year meets the published count, and flags appliances that saturate. Its docstring says the closed form gave 0.46 to 0.54 of the published cycles for TV and hob, and that CREST's reference implementation also calibrates iteratively ("bisects a `calibration_factor` against an annual consumption target"). | **MISSED**, although the transcript shows the session read this file |

**Consequence for the manuscript (our side, not the report's).** Our own code describes CREST's calibration two ways: a closed form (line 341) and an iterative bisection against annual energy (line 822). Eq. 12 as given in the prompt shows only the closed form, which is the **starting value** of the hazard, not the one used in production. When Eq. 12 is written into the Methods it should say that the closed-form hazard is then rescaled iteratively to the published cycles per year. Which of the two forms Richardson et al. (2010) Section 2.7 actually prints is something **only the author can settle, by opening Section 2.7.** The citation itself is safe: the transcript confirms a section titled "2.7 Appliance calibration scalars" was read. "Figure 3" is not confirmed.

### 1.5 Eq. 13: Jordan and Vajen Table 1 against our own PDF (check b)

Our copy: `Step9_docs/outputs_step9/sources/jordan_vajen_iea_task26_v2.0_2001.pdf`, md5 `c7c460924ef66588649b2473b706e2b9`, text extracted with `pdftotext -raw`, page 5:

```
Vdot in l/min 1 6 14 8
duration in min 1 1 10 5
inc/day 28 12 0.143 (once a week) 2
sigma 2 2 2 2
vol/load in l 1 6 140 40
vol/day in l 28 72 20 80 200
portion 0.14 0.36 0.10 0.40 1
Table 1: Assumptions and derived quantities for the load profile.
```

| Item | Report | Our PDF | State |
|---|---|---|---|
| All 30 Table 1 values (flow, duration, incidences, sigma, vol/load, vol/day, portion, sum 200) | as above | as above | **MATCH, every value** |
| Location | "p. 5, Table 1" | PDF page 5 | **MATCH** |
| 0.2 l/min discretisation | "page 4" | stated on page 3 ("Flow rates in steps of 0.2 l/min") and again in the Figure 1.2 caption on page 4 | **acceptable** |
| Title, version, date | "Realistic Domestic Hot-Water Profiles in Different Time Scales", V2.0, May 2001, Universität Marburg | title page identical ("FB. Physik, FG. Solar, Universität Marburg", "V. 2.0, May 2001") | **MATCH** |
| Calendar probability product | `P_year * P_weekday * P_day * P_holiday` | "prob = prob(year) * prob(weekday) * prob(day) * prob(holiday)", page 5 | **MATCH** |
| Sigma unit | "sigma (L/min) = 2" | the row reads `sigma 2 2 2 2`, **no unit printed** | **unit added by the report** |

The match is not independent evidence (the session read this same file from our repo), but it is now **confirmed by us against the PDF**, so these values may be cited.

**How our code uses the table (the report gets it wrong):** the report says flows are drawn "with standard deviation sigma = 2 L/min, discretised to steps of 0.2 L/min". Our code (`simulate_dhw_day`, lines 479-490) reads **sigma in units of the 0.2 l/min step**: `flow = rng.gauss(mean, sigma * 0.2)`, so sigma = 2 means **0.4 l/min**. This is a recorded decision (D-S9-2 item 6), made because reading sigma as 2 l/min gives negative draws for 31 % of category-A events and breaks Table 1's own 200 l/day. **The manuscript must describe our reading, not the report's.**

The hazard `h = N / (E - N*(d - 1))` with `N = 365 * inc/day` (times the per-dwelling scale) matches `calibrate_all` lines 704-712, and is again our own code comment handed back. The four driver activities stated (personal care, dish washing, food preparation) match `activity_appliance_map.csv` rows R0055-R0061.

**Jordan and Vajen (2001b), Solar Energy.** Crossref: *"Influence Of The DHW Load Profile On The Fractional Energy Savings:"* (title truncated in the record), Jordan and Vajen, Solar Energy 69, 197-208, 2001. The report prints a subtitle ("a case study of a solar combisystem for single-family houses") that the Crossref record does not contain; our PDF's own reference `/Jordan00/` gives the EuroSun 2000 conference version as "... A Case Study of a Solar Combisystem". Only the abstract was seen, so **whether it describes the same tapping model is unverified**, and the subtitle must be copied from the paper.

### 1.6 Eq. 10: Yeom et al. (2018) versus Shokri et al. (2017) (check c)

**Plausible, and marked AUTHOR OPENS.** Crossref confirms Yeom, Giacomelli, Fredrikson and Jha, *Privacy Risk in Machine Learning: Analyzing the Connection to Overfitting*, 2018 IEEE 31st CSF, pp. 268-282. The transcript shows **metadata only**; "pp. 270-272, Section III" was not read. The report's own addition, "superior to Shokri et al. 2017 **for autoregressive LLMs**", is not something a 2018 paper on classifiers can support and must not be written. Shokri stays as the general membership-inference citation (already in the paper).

**Carlini et al. (2022) carries two real errors:**

| Field | Report | Crossref |
|---|---|---|
| Pages | 2653-2670 | **1897-1914** |
| Third author | "Nasraheny, M." | **Nasr, Milad** |

The "pp. 2655-2658, Section 3.2" pointer lies outside the paper's own page range, so it cannot have been read (and the transcript confirms it was not downloaded). One further caution: our `G6.11` score is `NLL_base - NLL_tuned` against one public base model. Carlini et al. calibrate with shadow models trained with and without the target record, which is not the same thing. **Cite Carlini et al. for reporting TPR at a low FPR; describe the base-model difference as our own choice unless the author finds it printed there.**

### 1.7 Eq. 11: NNDR, Lowe (2004) and Park et al. (2018) (check d)

The transcript shows the session opened Park et al. and ran `'NNDR' in text`, **but not the result.** The report states Park defines DCR "in Section 5.3.1, p. 1078" and does not mention NNDR. That is plausible for a GAN paper on tables, and it is **unverified**. **Author opens Park et al., searches for "NNDR" and "nearest neighbour distance ratio", and confirms the DCR section.**

Lowe (2004): Crossref matches (IJCV 60(2) 91-110). Not downloaded. The ratio test is Lowe's, but a computer-vision citation is a detour in an Energy and Buildings methods section; it is optional.

Platzer and Reutterer (2021): Crossref matches (Frontiers in Big Data 4, 679939); opened per transcript. Its holdout comparison is also the logic of our `G6.13` clause "median DCR to train significantly below median DCR to test" (`tools/4thJ_step6_g613_dcr.py` line 9). **The priority claim "NNDR was introduced to tabular synthetic privacy by Platzer and Reutterer" is not supported by anything the report shows**; cite it as a work that *uses* DCR and NNDR with a holdout, never as the one that introduced NNDR.

### 1.8 Eq. 14: TABULA 3.0 W/m2 against our provenance file (check e)

Our `Step8_docs/outputs_step8/archetype_parameter_provenance.md` (lines 85-108) takes `phi_int = 3 W/m2` from `Tab.BoundaryCond` in `tabula-calculator.xlsx` (md5 `c99ddc9ffcb6dc0ae7391273d9619e37`), rows **`EU.SUH` and `EU.MUH`**, which every archetype we use points at. The national rows differ: `GB.Gen` 4, `IT.SUH` 2.8, `IT.MUH` 4.1, `ES` 3.

| Report says | State |
|---|---|
| "3.0 W/m2 is the standardized TABULA EU boundary condition (EU.SUH / EU.MUH)" | **correct, and copied from our provenance file** (the transcript shows it was read). Worth nothing as corroboration. |
| "tabulated in the TABULA Synthesis Report (Loga et al., 2012, Table 7), p. 25", "Read full text from PDF" | **unsupported.** No TABULA document was downloaded. |
| Reference: Loga, Diefenbach and Stein (2012), *Application of Building Typologies for Modelling the Energy Balance of the Residential Building Stock: Synthesis Report of the IEE Project TABULA*, URL `.../TABULA_FinalReport.pdf` | **unverified, and possibly two TABULA documents merged.** The title and the file name may not belong to the same report. Not checkable with the tools allowed here. |
| "Loga et al. (2016) mentions typologies" | not opened; the 2016 paper stays in the manuscript for the typologies, **not** for the 3.0 W/m2 value |

**What we can cite for 3.0 W/m2 without anyone opening anything is the file we actually used**: the TABULA calculator workbook, sheet `Tab.BoundaryCond`, rows `EU.SUH`/`EU.MUH`, with its download URL and access date from our provenance file. A claim that TABULA uses "a single density of about 3 W/m2 for residential buildings" is true **only for the EU comparison set**, not for the national rows, and should be worded that way.

### 1.9 Eq. 1: "exponential distance" and raking (check f)

The word "cross-entropy" does not occur in `RL34`. "Exponential distance" occurs three times (Section B row 1, Section C row 1, Section E Eq. 1), and the proposed manuscript sentence is *"calibration estimation under exponential distance (Deville and Sarndal, 1992, Section 1.3 and Table 1)"*.

**It is a loose name for raking, and it should not be printed.** In the Deville and Sarndal calibration family, raking ratio is the multiplicative case: the **weights** take an exponential form, and the **distance** being minimised is of the Kullback-Leibler (entropy) type between the calibrated and the starting weights. Calling it "exponential distance" mixes the calibration function with the distance, and "entropy" invites confusion with a different member of the same family. Also, our `rake()` stops at 0.5 percentage points (`MARGIN_TOL_PP`, line 47), so our weights approximate the raking solution; they are not the exact optimum. The manuscript's existing sentence (line 55: calibration estimators "minimise divergence from the donor weights subject to the margins (Deville and Sarndal, 1992)") is already correct, and needs no pointer the author has not checked. The report's "Section 1.3, Table 1, Case 2" was not read (the paper was not downloaded) and may not be printed.

### 1.10 Identities the report cannot fake (README step 4)

| Identity | Result |
|---|---|
| 21 recommended Crossref DOIs resolve | **21 / 21 resolve.** Titles, first authors, years, venues all match, except Carlini (pages, one author) |
| 2 arXiv DOIs resolve on DataCite | **2 / 2 resolve.** LoRA authors match. **Borisov et al.: DataCite lists Borisov, Seßler, Leemann, Pawelczyk, Kasneci (5 authors). The report prints 6, adding "Haug, J." and swapping the order.** |
| ISBN-13 check digits | Balinski and Young `978-0-300-02724-2` valid; Montgomery `978-0-470-54281-1` valid; Villani `978-0-8218-3312-4` valid; Levin 1st ed. `978-0-8218-4739-8` valid; **Levin 2nd ed. `978-1-4704-2962-0` INVALID** (the check digit must be 1) |
| No em or en dashes in the report | holds (0 found) |
| Section A: "No invented citations or phantom DOIs are recommended" | **no phantom DOI, but the sentence overstates**: one invented author name, one wrong author list, one invalid ISBN, one impossible page range |

---

## 2. Per-citation table

"Opened" = a full-text download appears in the transcript. AAO = ACCEPT AFTER AUTHOR OPENS. Pointers (page, section, equation) are **never** carried from this report unless the row says so.

| # | Citation (as in `RL34` Section H) | Eq. | DOI resolves | Metadata matches | Opened per transcript | Verdict | Reason |
|---|---|---|---|---|---|---|---|
| 1 | Balinski and Young (1982), *Fair Representation* | 2 | none (book; ISBN valid, not registry-checked) | not checkable | no | **AAO** | Standard source for Hamilton's method; "pp. 17-22, Chapter 3" came from secondary pages, not the book |
| 2 | Beckman, Baggerly and McKay (1996) | 2 | yes | yes | no | **ACCEPT** | Already cited, correct DOI already in the manuscript; the report's DOI "correction" is spurious |
| 3 | Borisov et al. (2023), GReaT | 15 | yes (DataCite) | **no**: author list differs (adds Haug; order wrong) | no | **AAO** | Right paper for the idea; copy the author list from DataCite |
| 4 | Carlini et al. (2022) | 10 | yes | **no**: pages 1897-1914, not 2653-2670; third author Nasr, not "Nasraheny" | no | **AAO** | Right paper for TPR at low FPR; the printed string is wrong in two fields |
| 5 | Deming and Stephan (1940) | 1 | yes | yes | no | **AAO** | Correct origin of IPF (our own guess, so no new information); page pointer unread |
| 6 | Deville and Sarndal (1992) | 1 | yes | yes | no | **ACCEPT** (as already cited) | Existing sentence stands; the new "Section 1.3, Table 1, Case 2" pointer and "exponential distance" wording are rejected |
| 7 | Hanley and McNeil (1982) | 10 | yes | yes | no | **AAO** | Standard AUC and Mann-Whitney reference; not read |
| 8 | Hu et al. (2022), LoRA | 16 | yes (DataCite; arXiv year 2021) | yes | yes (first 10 pages) | **ACCEPT** | Already cited; Eq. (3) in Section 4.1 lies in the pages read |
| 9 | Hyndman and Koehler (2006) | 3, 4 | yes | yes | yes (preprint) | **ACCEPT** | MAE and MAPE small-denominator problem; cite by section, not by the journal page numbers the preprint cannot give |
| 10 | Jordan and Vajen (2001a), IEA-SHC Task 26 report V2.0 | 13 | none (report) | yes, against our PDF title page | yes (our own copy) | **ACCEPT** | Table 1 checked value by value by us; URL not checked |
| 11 | Jordan and Vajen (2001b), Solar Energy 69 | 13 | yes | partly: vol, pages, year match; subtitle not in the Crossref record | no (abstract) | **AAO** | Whether it describes the same tapping model is unverified; take the subtitle from the paper |
| 12 | Levin, Peres and Wilmer (2009 / 2017) | 7 | none (book) | 1st-ed. ISBN valid; **2nd-ed. ISBN invalid** | yes (first 100 pages) | **ACCEPT** (1st edition) | Proposition 4.2 is in the pages read; cite one edition only, confirm its page |
| 13 | Lin (1991) | 8 | yes | yes | yes | **ACCEPT** | Original JSD source; the [0,1] bound pointer (p. 148) was in a document read, confirm before printing |
| 14 | Loga, Diefenbach and Stein (2012), TABULA Synthesis Report | 14 | none | not checkable; title and URL may be two documents | **no** | **REJECT** | Table 7 / p. 25 and "read full text" are unsupported; cite the calculator workbook we used instead |
| 15 | Loga, Stein and Diefenbach (2016) | 14 | yes | yes | no | **ACCEPT** (as already cited) | For TABULA typologies only, not for the 3.0 W/m2 value |
| 16 | Lovelace and Ballas (2013) | 2 | yes | yes | yes (arXiv) | **ACCEPT** | As the contrast (TRS is probabilistic); the "prompt said JASSS" story is false |
| 17 | Lowe (2004) | 11 | yes | yes | no | **AAO** (optional) | Origin of the ratio test; off-domain; "Section 7.1" unread |
| 18 | Montgomery, Peck and Vining (2012), 5th ed. | 5 | none (book; ISBN valid) | not checkable | no | **AAO** | Any OLS textbook serves; the equation numbers are unread |
| 19 | Park et al. (2018) | 11 | yes | yes | yes, but NNDR result not shown | **AAO** | Confirm the DCR section and that NNDR is absent before citing it for DCR only |
| 20 | Platzer and Reutterer (2021) | 11 | yes | yes | yes | **ACCEPT** | As a user of DCR and NNDR with a holdout, never as the originator of NNDR |
| 21 | Ramdas, Garcia Trillos and Cuturi (2017) | 6 | yes | yes (Crossref records the surname as "Trillos") | yes (arXiv) | **ACCEPT** (secondary) | "See also" for W1 in one dimension; Vallender remains the primary |
| 22 | Richardson, Thomson and Infield (2008) | 9 | yes | yes | yes | **ACCEPT** (already cited) | Note: its chain states are counts of active occupants, not activities |
| 23 | Richardson, Thomson, Infield and Clifford (2010) | 12 | yes | yes (positive control) | yes (Section 2.7) | **ACCEPT** (already cited) | Cite Section 2.7 for the calibration idea; the displayed "CREST equation" is ours, not theirs |
| 24 | Shokri et al. (2017) | 10 | yes | yes | no (abstract) | **ACCEPT** (already cited) | General membership-inference context only |
| 25 | Vallender (1974) | 6 | yes | yes | no | **AAO** | The title is the exact claim; "Theorem 1, Eq. (1)" unread |
| 26 | Villani (2003), *Topics in Optimal Transportation* | 6 | none (book; ISBN valid) | not checkable | no | **AAO** (optional) | Redundant with Vallender; "Theorem 2.18, p. 75" unread |
| 27 | Widen and Wackelgard (2010) | 9 | yes | yes | no | **AAO** (for the Eq. 9 claim) | Already cited elsewhere; "Section 2.1" and the first-order transition-count claim are unread |
| 28 | Willmott and Matsuura (2005) | 3 | yes | yes | no | **AAO** | Standard MAE reference; "p. 79, Eq. (1)" unread |
| 29 | Yeom et al. (2018) | 10 | yes | yes | no | **AAO** | Plausible loss-threshold source (check c); do not write "superior for LLMs" |

**Counts: 14 ACCEPT, 14 ACCEPT AFTER AUTHOR OPENS, 1 REJECT.**

---

## 3. What may enter the manuscript

Elsevier author-year strings, built from the Crossref / DataCite / PDF fields we retrieved, not from `RL34`'s Section H. No page or section pointer is included unless it was checked.

* Beckman, R.J., Baggerly, K.A., McKay, M.D., 1996. Creating synthetic baseline populations. Transportation Research Part A: Policy and Practice 30 (6), 415-429. https://doi.org/10.1016/0965-8564(96)00004-3 *(already cited, unchanged)*
* Deville, J.-C., Särndal, C.-E., 1992. Calibration estimators in survey sampling. Journal of the American Statistical Association 87 (418), 376-382. https://doi.org/10.1080/01621459.1992.10475217 *(already cited, existing sentence unchanged, no new pointer)*
* Hu, E.J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., Chen, W., 2022. LoRA: Low-rank adaptation of large language models. International Conference on Learning Representations (ICLR 2022). https://doi.org/10.48550/arXiv.2106.09685 *(already cited; Eq. (3), Section 4.1)*
* Hyndman, R.J., Koehler, A.B., 2006. Another look at measures of forecast accuracy. International Journal of Forecasting 22 (4), 679-688. https://doi.org/10.1016/j.ijforecast.2006.03.001
* Jordan, U., Vajen, K., 2001. Realistic Domestic Hot-Water Profiles in Different Time Scales, Version 2.0, May 2001. IEA Solar Heating and Cooling Programme, Task 26: Solar Combisystems. Universität Marburg, Marburg. *(already cited; Table 1, p. 5, values checked against our copy)*
* Levin, D.A., Peres, Y., Wilmer, E.L., 2009. Markov Chains and Mixing Times. American Mathematical Society, Providence, RI. ISBN 978-0-8218-4739-8. *(Proposition 4.2; confirm the page in this edition)*
* Lin, J., 1991. Divergence measures based on the Shannon entropy. IEEE Transactions on Information Theory 37 (1), 145-151. https://doi.org/10.1109/18.61115
* Loga, T., Stein, B., Diefenbach, N., 2016. TABULA building typologies in 20 European countries: Making energy-related features of residential building stocks comparable. Energy and Buildings 132, 4-12. https://doi.org/10.1016/j.enbuild.2016.06.094 *(already cited; typologies only)*
* Lovelace, R., Ballas, D., 2013. 'Truncate, replicate, sample': A method for creating integer weights for spatial microsimulation. Computers, Environment and Urban Systems 41, 1-11. https://doi.org/10.1016/j.compenvurbsys.2013.03.004
* Platzer, M., Reutterer, T., 2021. Holdout-based empirical assessment of mixed-type synthetic data. Frontiers in Big Data 4, 679939. https://doi.org/10.3389/fdata.2021.679939 *(wording: "as used by", never "introduced by")*
* Ramdas, A., García Trillos, N., Cuturi, M., 2017. On Wasserstein two-sample testing and related families of nonparametric tests. Entropy 19 (2), 47. https://doi.org/10.3390/e19020047 *(secondary only)*
* Richardson, I., Thomson, M., Infield, D., 2008. A high-resolution domestic building occupancy model for energy demand simulations. Energy and Buildings 40 (8), 1560-1566. https://doi.org/10.1016/j.enbuild.2008.02.006 *(already cited)*
* Richardson, I., Thomson, M., Infield, D., Clifford, C., 2010. Domestic electricity use: A high-resolution energy demand model. Energy and Buildings 42 (10), 1878-1887. https://doi.org/10.1016/j.enbuild.2010.05.023 *(already cited; Section 2.7 for the calibration idea, no equation number)*
* Shokri, R., Stronati, M., Song, C., Shmatikov, V., 2017. Membership inference attacks against machine learning models. 2017 IEEE Symposium on Security and Privacy (SP), 3-18. https://doi.org/10.1109/SP.2017.41 *(already cited)*

Also free to enter, because it is our own search, in the first person with the date: *we found no published precedent for the strict transfer-margin rule, for fictional-country perturbation of target margins as a test of conditional generation, or for redistributing a fixed annual internal-gain budget by an occupancy profile (searched 2026-09-23)*.

For the 3.0 W/m2 value, cite the data file we used, as our provenance file records it: *IWU (Institut Wohnen und Umwelt), TABULA calculator workbook `tabula-calculator.xlsx`, sheet `Tab.BoundaryCond`, rows `EU.SUH` and `EU.MUH`, https://episcope.eu/fileadmin/tabula/public/calc/tabula-calculator.xlsx* (access date from `archetype_parameter_provenance.md`).

---

## 4. Author must open before citing

1. **Richardson et al. (2010), Section 2.7.** Read what it actually prints for the calibration scalar: a closed form, or an iterative fit to annual energy. Then write Eq. 12 as *closed-form starting hazard, then rescaled iteratively to the published cycles per year* (`calibrate_to_published`, default 6 passes, 2 % tolerance), which is what production runs.
2. **Carlini et al. (2022).** Use the corrected string: Carlini, N., Chien, S., Nasr, M., Song, S., Terzis, A., Tramèr, F., 2022. Membership inference attacks from first principles. 2022 IEEE Symposium on Security and Privacy (SP), 1897-1914. https://doi.org/10.1109/SP46214.2022.9833649. Confirm the low-FPR convention section.
3. **Yeom et al. (2018)**, CSF, 268-282, https://doi.org/10.1109/csf.2018.00027. Confirm the loss-threshold adversary and its section.
4. **Hanley and McNeil (1982)**, Radiology 143 (1), 29-36, https://doi.org/10.1148/radiology.143.1.7063747. Confirm the AUC and Wilcoxon / Mann-Whitney equivalence.
5. **Park et al. (2018)**, PVLDB 11 (10), 1071-1083, https://doi.org/10.14778/3231751.3231757. Search for "NNDR" and "nearest neighbour distance ratio"; confirm the DCR section.
6. **Borisov et al. (2023)**. Use the DataCite author list: Borisov, V., Seßler, K., Leemann, T., Pawelczyk, M., Kasneci, G. https://doi.org/10.48550/arXiv.2210.06280. Confirm the serialisation section.
7. **Jordan and Vajen (2001b)**, Solar Energy 69, 197-208, https://doi.org/10.1016/s0038-092x(00)00154-7. Take the full subtitle from the paper; confirm it describes the Task 26 tapping model before citing it next to the report.
8. **Deming and Stephan (1940)**, Annals of Mathematical Statistics 11 (4), 427-444, https://doi.org/10.1214/aoms/1177731829.
9. **Willmott and Matsuura (2005)**, Climate Research 30, 79-82, https://doi.org/10.3354/cr030079.
10. **Vallender (1974)**, Theory of Probability and Its Applications 18 (4), 784-786, https://doi.org/10.1137/1118101. Confirm the CDF-integral statement and its number.
11. **Widen and Wackelgard (2010)**, Applied Energy 87 (6), 1880-1892, https://doi.org/10.1016/j.apenergy.2009.11.006. Confirm a first-order time-inhomogeneous chain estimated from transition counts, and its section, before citing it for Eq. 9.
12. **Balinski and Young (1982)**, Yale University Press. Confirm the chapter on Hamilton's (largest-remainder) method.
13. **Montgomery, Peck and Vining (2012)**, 5th ed., Wiley. Confirm the OLS slope and R-squared equation numbers, or use any OLS textbook the author already holds.
14. Optional: **Lowe (2004)**, IJCV 60 (2) 91-110, https://doi.org/10.1023/B:VISI.0000029664.99615.94, and **Villani (2003)**, AMS GSM 58. Both are redundant with better-placed sources.

**Also for whoever writes Eq. 13:** state that sigma = 2 is read as two steps of 0.2 l/min (0.4 l/min), a recorded decision (D-S9-2 item 6), not as 2 l/min. `RL34` Part 3 describes it wrongly.

---

## 5. Round-level verdict against the README's seven steps

| Step | Result |
|---|---|
| 1. Check its claims about our own work first | **FAILED.** Two invented errors in our prompt (§1.3); two wrong statements about our trigger code and one missed production loop (§1.4); wrong reading of our sigma (§1.5). |
| 2. Agreement with what we supplied tells us nothing | **As expected.** The CREST formula, our Eq. 12 and 13 formulas, the 3.0 W/m2 EU rows and all three OWN verdicts are our own text handed back. |
| 3. Check metadata columns, not value columns | **FAILED.** "Text Opened: Full text" is supported for 11 of 25; the "verified on disk" md5s are our own files (§1.2). |
| 4. Make it obey an identity it cannot fake | **MOSTLY HELD.** all 23 recommended DOIs resolve and the negative control returns 404; but Carlini's pages and one author, Borisov's author list, and one ISBN check digit fail (§1.10). |
| 5. Version and date rot | **Not the failure mode.** Nothing here is version-sensitive; URL reachability claims are undated and unverified. |
| 6. Expect the answer to inherit the prompt's framing | **PARTIAL.** Every candidate the prompt named was returned, but three were pushed back on (Shokri, Lovelace and Ballas, Park for NNDR). Those pushbacks are the useful part. |
| 7. Recommendations moving in the rescuing direction | **Mostly PASS.** Nothing here rescues a result. One flattering claim (our calibration "guarantees" what CREST's cannot) is wrong (§1.4). |

**What failed was, again, every claim of having read something. What held was document identity and the one table we could check against our own copy.** This round is a usable map of where each equation's source lives, not a set of page references.
