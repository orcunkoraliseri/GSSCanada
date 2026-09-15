# Manuscript Improvement Report & Remediation Action Plan

**Date:** 2026-09-14  
**Target Manuscript:** `4J_docs_occ/writing/submission/4J_manuscript_submission.md`  
**Built Form:** `4J_docs_occ/writing/submission/4J_manuscript_submission.docx`  
**Supplementary Material:** `4J_docs_occ/writing/submission/4J_supplementary_material.md`  
**Evaluation Origin:** `IMP_01_GEMINI_manuscript_evaluation.md` / `RIMP_01_2026-09-14.md`

---

## Executive Summary

The outward-facing forensic evaluation confirmed that the empirical and pre-registered core of the manuscript is exceptionally rigorous: the leave-one-country-out negative transfer result against the demographically raked real-donor null is methodologically sound, the hypotheses were md5-locked prior to training, and negative outcomes are reported without post-hoc rationalization.

However, the draft in its current state contains **several structural, bibliographic, and claims-calibration vulnerabilities** that pose immediate risks of **desk rejection** (editorial check) and **harsh reviewer rejection** (peer review). 

This report provides a prioritized, actionable roadmap to repair every identified defect before journal submission.

---

## Priority 1: Desk Reject Blockers (Immediate Repairs)

These defects violate basic editorial and integrity standards and must be resolved before any editor sends the paper out for review.

### 1.1 Fix Broken Table Numbering and Missing Gate Table
* **Defect:** Manuscript tables jump from Table 2 directly to Table 5. There is no Table 3 and no Table 4 in the document. Furthermore, Section 3 (lines 207-208) explicitly states: *"the complete gate set, with each band's provenance marked as published, project-chosen or heuristic, is given in Table 4."*
* **Root Cause:** Table 4 was moved or relegated to the Supplementary Material (Table S1) during drafting, but table numbering in the main text was not updated or renumbered.
* **Remediation Action:**
  1. Renumber all tables sequentially: Table 1, Table 2, Table 3 (formerly Table 5), Table 4 (formerly Table 6), Table 5 (formerly Table 7), Table 6 (formerly Table 8), Table 7 (formerly Table 9), Table 8 (formerly Table 10).
  2. Update line 208 in Section 3 to point directly to the Supplementary Material: *"the complete gate set... is given in Supplementary Table S1."*
  3. Verify all in-text table citations throughout the narrative to ensure every table reference matches the updated sequential numbering.

### 1.2 Repair Severe Citation Corruption (Vosoughkhosravi et al., 2023)
* **Defect:** In the Reference list (lines 1413-1415), the manuscript cites:  
  *Vosoughkhosravi, S., Dixon-Grasso, L., and Jafari, A. (2023). The impact of occupancy on building energy performance: a review. Energy and Buildings. DOI: 10.1016/j.enbuild.2023.113245*  
  Cross-referencing against CrossRef reveals a fatal metadata mismatch:
  * **Real Authors:** Sorena Vosoughkhosravi, Amirhosein Jafari, and Yimin Zhu (*Lesheena Dixon-Grasso is not an author on this paper*).
  * **Real Title:** *"Application of American time use survey (ATUS) in modelling energy-related occupant-building interactions: A comprehensive review"* (*not* "The impact of occupancy on building energy performance: a review").
  * **Missing Fields:** Volume 294, Article 113245.
* **Root Cause:** A literature database blend occurred between this review and an unrelated 2022 case study (*Vosoughkhosravi, Dixon-Grasso, & Jafari, 2022, Journal of Building Engineering*).
* **Remediation Action:** Replace the entry with the verified bibliographic record:  
  `Vosoughkhosravi, S., Jafari, A., and Zhu, Y. (2023). Application of American time use survey (ATUS) in modelling energy-related occupant-building interactions: A comprehensive review. Energy and Buildings, 294, 113245. DOI: 10.1016/j.enbuild.2023.113245`

### 1.3 Complete Placeholder Citations in Section 8 / References
* **Defect:** Lines 1419-1424 contain an editorial warning box (`To be completed before submission`) acknowledging that five foundational items are cited in the text without formatted entries:
  1. TABULA typology documentation set.
  2. Three national survey user guides (Spain INE 2009-10; UKTUS SN 8128; Italy ISTAT 2013-14).
  3. Eurostat HETUS methodological guidelines.
  4. The author's earlier single-country baseline publication.
* **Remediation Action:** Provide formal, complete citations for each of these entries and remove the warning banner. Specifically:
  * Insert the primary TABULA journal reference: `Loga, T., Stein, B., and Diefenbach, N. (2016). TABULA building typologies in 20 European countries - Making energy-related features of residential building stocks comparable. Energy and Buildings, 132, 4-12. DOI: 10.1016/j.enbuild.2016.06.094`
  * Add official statistical repository citations for INE, UK Data Service (SN 8128), and ISTAT.
  * Add the Eurostat Guidelines document: `Eurostat (2019). Guidelines for Harmonised European Time Use Surveys (HETUS) 2018 edition. Methodologies and Working Papers, Publications Office of the European Union, Luxembourg.`
  * Format the author's prior publication callout.

### 1.4 Rectify False Preamble Claim & Missing Bibliographic Metadata
* **Defect:** Line 1377-1378 asserts: *"Every DOI below was resolved against CrossRef during the pipeline's citation checks."* In reality, 6 of the 12 formatted references have no DOI listed, and several omit volume, page numbers, or publication years.
* **Remediation Action:** Add the verified CrossRef DOIs and complete metadata for:
  * `Richardson, I., Thomson, M., and Infield, D. (2008). Energy and Buildings, 40(8), 1560-1566. DOI: 10.1016/j.enbuild.2008.02.006`
  * `Richardson, I., Thomson, M., Infield, D., and Clifford, C. (2010). Energy and Buildings, 42(10), 1878-1887. DOI: 10.1016/j.enbuild.2010.05.023`
  * `Widén, J., and Wäckelgård, E. (2010). Applied Energy, 87(6), 1880-1892. DOI: 10.1016/j.apenergy.2009.11.006`
  * `Lombardi, F., Balderrama, S., Quoilin, S., and Colombo, E. (2019). Energy, 177, 433-444. DOI: 10.1016/j.energy.2019.04.097` (*correct year from 2020 to 2019*).
  * `Osman, M., and Ouf, M. (2021). Building and Environment, 196, 107785. DOI: 10.1016/j.buildenv.2021.107785` (*restore full subtitle*).
  * `Pflugradt, N. (2016). Modellierung von Wasser- und Energieverbräuchen in Haushalten. Doctoral dissertation, Technische Universität Chemnitz.` (*correct venue from "LoadProfileGenerator"*).
  * `Jordan, U., and Vajen, K. (2001). Realistic domestic hot-water profiles in different time scales. IEA SHC Task 26 Technical Report, Universität Marburg.` (*add year 2001 and Task 26 series*).
  * Remove `Beckman, R. J., Baggerly, K. A., and McKay, M. D. (1996)` or insert a citation callout to it in Section 1.2.

---

## Priority 2: Substantive Claims & Textual Calibration (Reviewer Reject Defense)

These issues represent substantive vulnerabilities that technical reviewers will identify and challenge during peer review.

### 2.1 Reconcile Table 9 Caption, Scales, and Geographic Scope
* **Defect:** Table 9 is titled *"Stock appliance-electricity peak, generated populations"*, quoting power levels of 503 W (Spain), 404 W (Italy), and 416 W (Britain). 
  * Values around 400-500 W are per-dwelling average electrical draw, not the aggregated electrical peak of a multi-thousand building stock (which would be in megawatts).
  * Section 4.4 explicitly states that the stock-scale end-use campaign was conducted only on London (7,602 flats) and Bologna (29,902 flats), whereas Spain had zero stock end-use cells.
* **Remediation Action:**
  * Update Table 9 caption to accurately reflect the data scale: *"Mean per-dwelling appliance-electricity peak hour and power, archetype-scale generated populations."*
  * In Section 5.8 prose, clarify that Spain's values are measured on the archetype campaign, whereas stock-scale end-use confirmation was conducted on the London and Bologna districts.

### 2.2 Correct Age Bands Mislabelled as "Activity Bands"
* **Defect:** Section 2.2 (lines 170-171) states: *"Those three are the activity bands reported throughout §5.1."* Section 5.1 (lines 605-606 and line 623) repeats: *"per activity band, per fold"* and *"wins every activity band"*.
* **Reality:** The categories `Y25-44`, `Y45-64`, and `Y_GE65` are demographic **age bands**, not activity bands.
* **Remediation Action:** Edit Section 2.2 and Section 5.1 to replace "activity bands" with "age bands" everywhere this comparison is described.

### 2.3 Temper Universal Claims Regarding Model Capacity
* **Defect:** Abstract, Highlights, and Section 5.3 claim that *"Capacity is eliminated as the explanation from three independent directions"*.
* **Vulnerability:** Reviewers will note that:
  1. Backbone scaling compares only two points (1.48B vs 7.30B), which cannot establish an empirical scaling law.
  2. Full fine-tuning (92x parameter increase) was evaluated on **only one fold**.
  3. The alternative model family was evaluated on **only one fold**.
  4. In the era of 70B+ frontier models, 7.3B is modest.
* **Remediation Action:** Reframe Section 5.3 and the Abstract:
  * State clearly that within the tested parameter regime (1.5B to 7.3B, low-rank adapter vs full parameter tuning on Fold 1, and across two distinct model families), capacity scaling did not resolve the transfer gap.
  * Avoid asserting that capacity is universally eliminated for all language models.

### 2.4 Transparently Qualify the Steering vs. Amplitude Finding
* **Defect:** The paper frequently highlights as a core diagnostic contribution: *"the model steers correctly and delivers about half the amplitude"*. However:
  * Steering R-squared (0.85 to 0.98) was measured **only on the 1.48B pilot arm** and was never recomputed on the reported 7.30B model (as admitted in Section 5.4 and Section 7.10).
  * Amplitude slope on the 7.30B model pooled six conditioning channels, departing from the pre-registered five-channel protocol.
* **Remediation Action:**
  * **Option A (Preferred):** Re-run the fictional-country steering evaluation on the frozen 7.30B weights and report the actual measured R-squared alongside the registered five-channel amplitude slope.
  * **Option B:** Rephrase Abstract line 5, Section 1.5, and Section 6.2 to explicitly specify that steering was demonstrated on the pilot architecture and inherited as a qualitative finding, rather than presenting it as an established property of the 7.30B model.

### 2.5 Add In-Text Callout for Figure 2
* **Defect:** Figure 2 (Leave-one-country-out design and the two nulls) is rendered after line 100, but no sentence in the body text of Section 1, 3, or 4 points the reader to it.
* **Remediation Action:** Insert an explicit callout in Section 1.5 (e.g., *"The leave-one-country-out partition and the comparative relationship to the two null baselines are illustrated in Figure 2."*) or in Section 3.5.

### 2.6 Revise Table 1 Lineage Characterization
* **Defect:** Table 1 awards affirmative checkmarks (`✓`) to Osman and Ouf (2021) and Vosoughkhosravi et al. (2023) for "Generative model" and "Stock-scale simulation", even though both are literature reviews.
* **Remediation Action:** Distinguish primary modeling studies from review papers in Table 1 (e.g., using a footnote, designated symbol, or labeling them as review scopes).

---

## Priority 3: Methodological Fortification & Reviewer Defenses

Anticipating predictable technical demands from reviewers in building energy simulation and applied machine learning.

### 3.1 Essential Missing Foundational Citations
Ensure that the literature positioning includes foundational citations with verified DOIs:
1. **Building Typology:** `Loga, T., Stein, B., and Diefenbach, N. (2016). TABULA building typologies in 20 European countries - Making energy-related features of residential building stocks comparable. Energy and Buildings, 132, 4-12. DOI: 10.1016/j.enbuild.2016.06.094`
2. **Building Simulation Engine:** `Crawley, D. B., Lawrie, L. K., Winkelmann, F. C., Buhl, W. F., Huang, Y. J., Pedersen, C. O., Strand, R. K., Liesen, R. J., Fisher, D. E., Witte, M. J., and Glazer, J. (2001). EnergyPlus: creating a new-generation building energy simulation program. Energy and Buildings, 33(4), 319-331. DOI: 10.1016/s0378-7788(00)00114-6`
3. **Privacy & Membership Inference:** `Shokri, R., Stronati, M., Song, C., and Shmatikov, V. (2017). Membership Inference Attacks Against Machine Learning Models. 2017 IEEE Symposium on Security and Privacy (SP), 3-18. DOI: 10.1109/sp.2017.41`
4. **Stochastic Occupancy Baseline:** `Wilke, U., Haldi, F., Scartezzini, J.-L., and Robinson, D. (2013). A bottom-up stochastic model to predict building occupants' time-dependent activities. Building and Environment, 60, 254-264. DOI: 10.1016/j.buildenv.2012.10.021`
5. **PEFT Foundation:** `Hu, E. J., et al. (2022). LoRA: Low-Rank Adaptation of Large Language Models. ICLR 2022.`

### 3.2 Proactive Explanations for Known Modeling Choices
Reviewers will probe specific modeling assumptions; adding clarifying sentences in Section 3 and Section 7 will neutralize these objections before they are raised:
* **Single Training Seed:** Add a clarifying sentence in Section 7.8 acknowledging that while training was conducted with a fixed random seed per fold, sampling-noise probes on frozen weights confirmed that variance across seeds is bounded.
* **Secondary Activity Load Suppression:** Clarify in Section 3.9 and Section 5.9 why primary-only activity triggering was retained (strict alignment with the CREST/RAMP ancestral lineage) despite suppressing laundry loads by 80-90%.
* **Day-Chaining Independence:** State explicitly in Section 3.6 why independent daily resampling was chosen over multi-day Markov transitions (empirical sensitivity tests showed peak demand moved by <0.24%, well below seed noise).
* **LoRA Merge Drift:** Note in Section 7.8 that while merged and unmerged weights exhibit numerical drift, the aggregate distribution of generated token sequences remains within the same statistical envelope.

---

## Actionable Execution Checklist

| Step | Item | Target File & Section | Status |
|:---:|---|---|:---:|
| 1 | Renumber tables sequentially (Tables 1-8); update Table 4 pointer to Table S1 | `4J_manuscript_submission.md`, §3 & all tables | Pending |
| 2 | Correct Vosoughkhosravi citation (real authors, ATUS review title, Vol 294) | `4J_manuscript_submission.md`, References | Pending |
| 3 | Replace Section 8 warning block with complete citations (TABULA, HETUS, 3 survey guides) | `4J_manuscript_submission.md`, References | Pending |
| 4 | Add missing DOIs to Richardson (2008, 2010), Widén (2010), Lombardi (2019), Osman (2021) | `4J_manuscript_submission.md`, References | Pending |
| 5 | Correct Pflugradt (2016) doctoral dissertation metadata & Jordan & Vajen (2001) report data | `4J_manuscript_submission.md`, References | Pending |
| 6 | Remove orphan reference Beckman (1996) or add in-text callout in §1.2 | `4J_manuscript_submission.md`, §1.2 / References | Pending |
| 7 | Correct "activity bands" to "age bands" | `4J_manuscript_submission.md`, §2.2, §5.1, Table 5 | Pending |
| 8 | Align Table 9 caption & text to "per-dwelling archetype scale" and clarify Spain's scope | `4J_manuscript_submission.md`, §5.8, Table 9 | Pending |
| 9 | Insert in-text callout to Figure 2 | `4J_manuscript_submission.md`, §1.5 | Pending |
| 10 | Temper universal capacity claims to the tested empirical regime | `4J_manuscript_submission.md`, Abstract, §5.3, §6.1 | Pending |
| 11 | Rebuild Word document `4J_manuscript_submission.docx` to mirror all markdown edits | `4J_manuscript_submission.docx` | Pending |
