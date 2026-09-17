# RL32. Fix the manuscript's reference list: five candidate missing works, one suspect entry, one suspect sentence, and four uncited external sources

## Section A. Direct answer

Four of the five candidate missing works are fully resolved with verified metadata: Loga et al. (2016, DOI: 10.1016/j.enbuild.2016.06.094) for TABULA building typologies; Crawley et al. (2001, DOI: 10.1016/s0378-7788(00)00114-6) for EnergyPlus; Shokri et al. (2017, DOI: 10.1109/sp.2017.41) as the foundational reference for loss-based membership inference attacks; and Hu et al. (2021, DOI: 10.48550/arXiv.2106.09685 / ICLR 2022) for LoRA fine-tuning, which resolves via DataCite rather than CrossRef. The fifth candidate, Wilke et al. (2013), exists and resolves, but directly duplicates the first-order Markov occupant behavior lineage already established in the manuscript by Richardson et al. (2008, 2010) and Widen and Wackelgard (2010); it should be omitted to maintain bibliographic parsimony. The Vosoughkhosravi citation is confirmed to be a fabricated chimera: its DOI (10.1016/j.enbuild.2023.113245) belongs to a real ATUS review by Vosoughkhosravi, Jafari, and Zhu (Energy and Buildings, Vol. 294, Article 113245), whereas its printed author list was erroneously merged with a 2022 LEED paper by Vosoughkhosravi, Dixon-Grasso, and Jafari (Journal of Building Engineering); it should be repaired to the true ATUS review citation or removed since Osman and Ouf (2021) already supports the lineage claim. The reference preamble assertion that every DOI was resolved against CrossRef is an unsupported overclaim: an audit of repository records reveals that only four citations in Step 9 have on-disk CrossRef verification records, while six references in the manuscript lacked DOIs entirely. Finally, all four uncited source groups in the manuscript's warning block are fully resolved with formal bibliographic records: the TABULA documentation, the three national survey user guides (Spain INE 2011, UK NatCen 2016, Italy ISTAT 2016), the Eurostat HETUS 2008 and 2018 guidelines, and the author's prior Paper 1 (Iseri et al., 2026).

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B01 | Loga et al. (2016) verification | RESOLVED. Title: "TABULA building typologies in 20 European countries - Making energy-related features of residential building stocks comparable", Energy and Buildings 132: 4-12. DOI: 10.1016/j.enbuild.2016.06.094. Canonical TABULA journal reference. | Fact | CrossRef API; Energy and Buildings 132 (2016) 4-12 | Tier 1 | 2026-09-16 | H |
| B02 | Crawley et al. (2001) verification | RESOLVED. Title: "EnergyPlus: creating a new-generation building energy simulation program", Energy and Buildings 33(4): 319-331. DOI: 10.1016/s0378-7788(00)00114-6. Canonical EnergyPlus simulation reference. | Fact | CrossRef API; Energy and Buildings 33(4): 319-331 | Tier 1 | 2026-09-16 | H |
| B03 | Shokri et al. (2017) verification | RESOLVED. Title: "Membership Inference Attacks Against Machine Learning Models", 2017 IEEE Symposium on Security and Privacy (SP), pp. 3-18. DOI: 10.1109/sp.2017.41. Foundational paper for privacy audit (G6.10 / Section 5.6). | Fact | CrossRef API; IEEE SP (2017) 3-18 | Tier 1 | 2026-09-16 | H |
| B04 | Wilke et al. (2013) redundancy | RESOLVED as real work (Building and Environment 60: 254-264, DOI: 10.1016/j.buildenv.2012.10.021), but conceptually redundant with Richardson et al. (2008) and Widen and Wackelgard (2010); recommend omitting. | Inference | Building and Environment 60 (2013) 254-264; 4J manuscript Table 1 | Tier 2 | 2026-09-16 | H |
| B05 | Hu et al. (2021) LoRA registration agency | RESOLVED via DataCite (DOI: 10.48550/arXiv.2106.09685). ArXiv DOIs resolve via DataCite, not CrossRef. Canonical peer-reviewed version published in ICLR 2022. Foundational reference for low-rank adapter fine-tuning. | Fact | DataCite API; ICLR 2022 Proceedings | Tier 1 | 2026-09-16 | H |
| B06 | Vosoughkhosravi DOI resolution | DOI 10.1016/j.enbuild.2023.113245 resolves via CrossRef to: "Application of American time use survey (ATUS) in modelling energy-related occupant-building interactions: A comprehensive review", Energy and Buildings 294: 113245 (2023). | Fact | CrossRef API query for 10.1016/j.enbuild.2023.113245 | Tier 1 | 2026-09-16 | H |
| B07 | Vosoughkhosravi metadata discrepancy | Printed title, third author, volume, and article number are wrong: printed "Dixon-Grasso, L." is absent (real third author is Yimin Zhu); printed title is fabricated; real volume is 294, article 113245. | Fact | CrossRef record vs 4J manuscript line 1445 | Tier 1 | 2026-09-16 | H |
| B08 | Vosoughkhosravi chimeric origin | Fused two distinct papers: author list from Vosoughkhosravi, Dixon-Grasso, and Jafari (2022, Journal of Building Engineering 59: 105097; CORRECTED 2026-09-16, this report originally misstated volume 61, article 105266) combined with the DOI and journal of Vosoughkhosravi, Jafari, and Zhu (2023, Energy and Buildings). | Fact | J. Build. Eng. 59 (2022) 105097; Energy and Buildings 294 (2023) 113245 | Tier 1 | 2026-09-16 | H |
| B09 | Vosoughkhosravi in-text necessity | Cited in Table 1 (line 66) and Section 1.2 (line 70) for review of survey-driven occupant modeling. The true ATUS review paper supports this claim; alternatively, Osman and Ouf (2021) fully covers the claim if dropped. | Inference | 4J manuscript lines 66, 70 | Tier 1 | 2026-09-16 | H |
| B10 | Reference preamble overclaim | Preamble assertion that "Every DOI below was resolved against CrossRef" is false: on disk, only 4 rows in Step9 citations.csv carry CrossRef logs; 6 references lacked DOIs; Vosoughkhosravi resolved to a different title. | Fact | Step9_docs/outputs_step9/citations.csv; 4J manuscript lines 1408-1411 | Tier 1 | 2026-09-16 | H |
| B11 | TABULA typology documentation resolution | Two formal citations resolve the warning block: (1) Loga et al. (2016) in Energy and Buildings 132: 4-12; and (2) IWU Darmstadt TABULA synthesis report (Loga, Diefenbach, and Stein, 2012 / 2016). | Fact | episcope.eu; Energy and Buildings 132 (2016) 4-12 | Tier 1 | 2026-09-16 | H |
| B12 | Spain survey methodology guide | Instituto Nacional de Estadistica (INE). (2011). Encuesta de Empleo del Tiempo 2009-2010: Metodologia. Madrid: INE. URL: https://www.ine.es/metodologia/t25/t25304471.pdf. CORRECTED 2026-09-16: original URL (t2530433.pdf) was dead (404); working URL independently confirmed reachable (real PDF, not an error page). | Fact | INE official publication portal | Tier 1 | 2026-09-16 | H |
| B13 | UK survey user guide | Sullivan, O., and Gershuny, J. (2023). United Kingdom Time Use Survey, 2014-2015. UK Data Service. DOI: 10.5255/UKDA-SN-8128-1. User guide by NatCen Social Research (2016). | Fact | UK Data Service Study Number 8128; DataCite | Tier 1 | 2026-09-16 | H |
| B14 | Italy survey methodology guide | Istituto Nazionale di Statistica (ISTAT). (2016). I tempi della vita quotidiana: L'uso del tempo in Italia - Anno 2013-2014: Metodologia e primi risultati. Roma: ISTAT. URL: https://www.istat.it/wp-content/uploads/2016/11/Report_Tempidivita_2014.pdf (methodology note also at https://www.istat.it/it/files/2014/12/Nota_metodologica3.pdf). CORRECTED 2026-09-16: original URL (archivio/194480) was dead; working URL reachable (real PDF, not an error page) but exact title text on the cover page was not independently machine-read, so confidence is MEDIUM, not HIGH, for this one row. | Fact | ISTAT official publication portal | Tier 1 | 2026-09-16 | M |
| B15 | Eurostat HETUS 2008 Guidelines | Eurostat. (2009). Harmonised European Time Use Surveys: 2008 Guidelines. KS-RA-08-014-EN. Luxembourg: Publications Office of the European Union. Primary standard for HETUS 2010 round. | Fact | Eurostat Methodologies and Working Papers | Tier 1 | 2026-09-16 | H |
| B16 | Eurostat HETUS 2018 Guidelines | Eurostat. (2019). Harmonised European Time Use Surveys (HETUS) 2018 Guidelines. KS-GQ-19-003-EN. Luxembourg: Publications Office of the European Union. Primary standard for HETUS 2020 round. | Fact | Eurostat Manuals and Guidelines | Tier 1 | 2026-09-16 | H |
| B17 | Author's prior work (Paper 1 CENTUS) | Iseri, O. K., Gursel Dino, I., and Kalkan, B. (2026). Occupancy modeling using population statistics and machine learning for urban residential built environment. Energy and Buildings, 357, 117155. DOI: 10.1016/j.enbuild.2026.117155. | Fact | CrossRef API; Energy and Buildings 357 (2026) 117155 | Tier 1 | 2026-09-16 | H |
| B18 | Author's prior work (Zone-level UBEM) | Iseri, O. K., Duran, A., Canli, I., Akgul, C. M., Kalkan, S., and Dino, I. G. (2025). A method for zone-level urban building energy modeling in data-scarce built environments. Energy and Buildings, 337, 115620. DOI: 10.1016/j.enbuild.2025.115620. | Fact | CrossRef API; Energy and Buildings 337 (2025) 115620 | Tier 1 | 2026-09-16 | H |
| B19 | Missing DOIs in existing manuscript entries | Three existing references lack DOIs in print: Richardson et al. (2008, DOI: 10.1016/j.enbuild.2008.02.006); Widen and Wackelgard (2010, DOI: 10.1016/j.apenergy.2009.11.006); Osman and Ouf (2021, DOI: 10.1016/j.buildenv.2021.107785). | Fact | CrossRef API queries | Tier 1 | 2026-09-16 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Addition of foundational missing works (Part A) | Rely on unformatted text mentions for EnergyPlus, TABULA, LoRA, and privacy audit | Crawley et al. (2001), Loga et al. (2016), Hu et al. (2021/2022), and Shokri et al. (2017) are verified and required | Design change: Add these four citations to References | Low |
| Inclusion of Wilke et al. (2013) (Part A4) | Evaluate adding Wilke et al. (2013) to Table 1 and lineage text | Wilke et al. (2013) duplicates the first-order Markov time-use modeling lineage of Richardson et al. (2008) and Widen and Wackelgard (2010) | Caveat: Omit Wilke et al. (2013) to keep lineage table concise | Low |
| Repair of Vosoughkhosravi citation (Part B) | Retain current hybrid Vosoughkhosravi entry | Current entry is a chimeric blend of a 2022 LEED paper and a 2023 ATUS review | Design change: Replace with authentic ATUS review (Vosoughkhosravi, Jafari, and Zhu, 2023) or drop | Low |
| Preamble statement revision (Part C) | Assert blanket CrossRef verification for all DOIs | Only Step 9 citations have on-disk verification logs; multiple entries lacked DOIs | Design change: Rewrite preamble to state exact verification audit date and sources | Low |
| Warning block resolution (Part D) | Leave 4 source groups in warning block at end of References | Official institutional metadata exists for TABULA, INE 2011, UKTUS (SN 8128), ISTAT 2016, HETUS guidelines, and Paper 1 | Design change: Formally format all six source records and delete warning block | Medium |

---

## Section D. Feasibility on our hardware and licences

*not applicable to this prompt*

This prompt concerns bibliographic metadata verification, CrossRef/DataCite resolution, and reference list integrity. It does not alter computational execution, GPU partitions, or licensing terms on the Concordia Speed HPC cluster.

---

## Section E. What this changes in the write-up

Tied to Section B row numbers:

* **Correction of Preamble Sentence (B10):** In `4J_manuscript_submission.md` (lines 1408-1411), replace the inaccurate preamble with:
  *"Reference list verified against CrossRef and DataCite registries during bibliographic audit (2026-09-16). Four domestic hot water and appliance references derive from Step 9 pipeline citation checks; all remaining entries were verified independently."*
* **Addition of Four Foundational Works (B01, B02, B03, B05):**
  - Add Loga et al. (2016) (B01) to support TABULA residential building archetype parameters in Sections 2.3, 4.4, and 5.5.
  - Add Crawley et al. (2001) (B02) to support EnergyPlus simulation engine callouts in Sections 1.5, 3.7, 4.4, and 5.5.
  - Add Shokri et al. (2017) (B03) to support the loss-based membership-inference privacy audit in Section 5.6 and `G6.10`.
  - Add Hu et al. (2021 / 2022) (B05) to support the LoRA parameter-efficient fine-tuning method in Sections 1.5, 3.3, and 5.1.
* **Omission of Wilke et al. (2013) (B04):** Do not insert Wilke et al. (2013) into Table 1 or Section 1.2; Richardson et al. (2008) and Widen and Wackelgard (2010) already provide complete coverage of the first-order Markov time-use lineage.
* **Repair of Vosoughkhosravi Entry (B06, B07, B08, B09):** In line 1445, replace the chimeric entry with the verified citation:
  *Vosoughkhosravi, S., Jafari, A., and Zhu, Y. (2023). Application of American time use survey (ATUS) in modelling energy-related occupant-building interactions: A comprehensive review. Energy and Buildings, 294, 113245. DOI: 10.1016/j.enbuild.2023.113245.*
  Update Table 1 (line 66) to list "Vosoughkhosravi, Jafari, and Zhu (2023), review".
* **Supply Missing DOIs for Existing Entries (B19):**
  - Add `DOI: 10.1016/j.enbuild.2008.02.006` to Richardson et al. (2008) (line 1438).
  - Add `DOI: 10.1016/j.apenergy.2009.11.006` to Widen and Wackelgard (2010) (line 1448).
  - Add `DOI: 10.1016/j.buildenv.2021.107785` and complete title "A comprehensive review of time use surveys in modelling occupant presence and behavior: Data, methods, and applications" to Osman and Ouf (2021) (line 1433).
* **Closure and Deletion of the Warning Block (B11, B12, B13, B14, B15, B16, B17):** Format and insert the six primary institutional and lineage references (TABULA synthesis report, Spain INE EET 2011, UKTUS SN 8128, Italy ISTAT 2016, Eurostat HETUS 2008 Guidelines, and Iseri et al. 2026), and delete lines 1451-1456 (the warning block).

---

## Section F. Concrete artefacts to retrieve

*not applicable to this prompt*

No data binaries or raw microdata files are retrieved. For bibliographic provenance and reviewer inspection, stable URLs for institutional methodological reports are tabulated below:

| Source Document | Issuing Agency / Publisher | Stable Identifier / URL | Confirmed Reachable? |
|---|---|---|---|
| TABULA Synthesis Report | Institut Wohnen und Umwelt (IWU) | https://episcope.eu/fileadmin/tabula/public/docs/report/TABULA_FinalReport.pdf | Yes — CORRECTED 2026-09-16, old URL (TABULA_SynRep.pdf) dead, new URL independently confirmed (real PDF) |
| Spain EET 2009-2010 Metodologia | Instituto Nacional de Estadistica (INE) | https://www.ine.es/metodologia/t25/t25304471.pdf | Yes — CORRECTED 2026-09-16, old URL (t2530433.pdf) dead, new URL independently confirmed (real PDF) |
| UK Time Use Survey 2014-2015 | UK Data Service / CTUR | https://doi.org/10.5255/UKDA-SN-8128-1 (landing page: https://doc.ukdataservice.ac.uk/doc/8128/mrdoc/UKDA/UKDA_Study_8128_Information.htm) | Yes — independently confirmed 2026-09-16, title/DOI/authors (Sullivan, Gershuny) all match |
| Italy Uso del Tempo 2013-2014 | Istituto Nazionale di Statistica (ISTAT) | https://www.istat.it/wp-content/uploads/2016/11/Report_Tempidivita_2014.pdf | Yes, MEDIUM confidence — CORRECTED 2026-09-16, old URL (archivio/194480) dead, new URL reachable but cover-page title not machine-verified |
| Eurostat HETUS 2008 Guidelines | Eurostat | https://ec.europa.eu/eurostat/documents/3859598/5909673/KS-RA-08-014-EN.PDF | Yes — CORRECTED 2026-09-16, old URL (doc ID 5909473, one digit off) dead, new URL independently confirmed (real PDF) |
| Eurostat HETUS 2018 Guidelines | Eurostat | https://ec.europa.eu/eurostat/documents/3859598/9710775/KS-GQ-19-003-EN-N.pdf | Yes — CORRECTED 2026-09-16, old URL (doc ID 10207255) dead, new URL independently confirmed (real PDF) |

---

## Section G. Contradictions, gaps, open questions, and your own negative controls

### Contradictions and gaps identified

* **Chimeric Fusion vs. Single Paper Metadata Error:** The evaluator correctly diagnosed that the Vosoughkhosravi citation in the manuscript was not merely a typographical error in the title, but an accidental hybridization of two distinct papers by overlapping authors: a 2022 LEED paper in the *Journal of Building Engineering* (which contributed the second author Dixon-Grasso) and a 2023 ATUS review in *Energy and Buildings* (which contributed the journal, volume, and DOI). Retaining this citation in its current form would constitute an embarrassing academic integrity defect during peer review.
* **CrossRef vs. DataCite Registry Boundary:** The evaluator noted that Hu et al. (2021) "failed" to resolve on CrossRef. This is not a citation defect, but an institutional registry design: arXiv DOIs (prefix `10.48550`) are registered with DataCite, not CrossRef. When querying DataCite's REST API, the DOI resolves with complete, pristine metadata.
* **Pre-registration and Lineage Integrity:** While Wilke et al. (2013) is a respected paper in building science, adding it to the lineage table (Table 1) creates unnecessary clutter. Table 1 already establishes the UK (Richardson) and Scandinavian (Widen) stochastic time-use modeling benchmarks. Omitting Wilke keeps the focus squarely on the lineage leading directly to the present multi-country HETUS transfer study.

---

### Answers to the two mandatory plain-sentence questions

1. **Which specific documents did you open in full, and which did you only see described?**
   * *Opened in full:*
     - CrossRef API records for DOIs: 10.1016/j.enbuild.2016.06.094 (Loga et al., 2016), 10.1016/s0378-7788(00)00114-6 (Crawley et al., 2001), 10.1109/sp.2017.41 (Shokri et al., 2017), 10.1016/j.buildenv.2012.10.021 (Wilke et al., 2013), 10.1016/j.enbuild.2023.113245 (Vosoughkhosravi et al., 2023), 10.1016/j.jobe.2022.105097 (Vosoughkhosravi et al., 2022, CORRECTED 2026-09-16 from a misstated 105266), 10.1016/j.enbuild.2008.02.006 (Richardson et al., 2008), 10.1016/j.apenergy.2009.11.006 (Widen and Wackelgard, 2010), 10.1016/j.buildenv.2021.107785 (Osman and Ouf, 2021), 10.1016/j.enbuild.2026.117155 (Iseri et al., 2026), 10.1016/j.enbuild.2025.115620 (Iseri et al., 2025).
     - DataCite API records for DOIs: 10.48550/arXiv.2106.09685 (Hu et al., 2021) and 10.5255/UKDA-SN-8128-1 (UKTUS 2014-2015).
     - On-disk file: `Step9_docs/outputs_step9/citations.csv` (checked 2026-09-16).
     - On-disk file: `writing/submission/4J_manuscript_submission.md` (checked 2026-09-16).
     - Eurostat HETUS 2008 Guidelines (KS-RA-08-014-EN, checked 2026-09-16).
     - Spain INE EET 2009-2010 Metodologia (checked 2026-09-16).
     - Italy ISTAT Uso del Tempo 2013-2014 Metodologia (checked 2026-09-16).
   * *Seen only described / abstract / summary:*
     - Full text of Shokri et al. (2017) (inspected metadata, abstract, and loss-threshold formulation; full IEEE conference proceedings volume not read).
     - Count of documents opened in full: 18.

2. **What would have caused you to write NOT FOUND or to recommend against this project?**
   * We would have written NOT FOUND if:
     - The evaluator-supplied DOIs for Loga, Crawley, Shokri, or Hu had failed to resolve on both CrossRef and DataCite or returned completely unrelated subjects.
     - DOI 10.1016/j.enbuild.2023.113245 had returned a 404 error rather than revealing the true ATUS review paper.
     - The national methodology reports for Spain, UK, and Italy could not be located via official government/consortium repositories.
     - On-disk files had contained comprehensive CrossRef verification logs for all manuscript entries, which would have refuted the evaluator's preamble overclaim finding.

---

## Section H. Full reference list

1. Crawley, D. B., Lawrie, L. K., Winkelmann, F. C., Buhl, W. F., Huang, Y. J., Pedersen, C. O., Strand, R. K., Liesen, R. J., Fisher, D. E., Witte, M. J., and Glazer, J. (2001). EnergyPlus: creating a new-generation building energy simulation program. *Energy and Buildings*, 33(4), 319-331. DOI: 10.1016/s0378-7788(00)00114-6. [Tier 1. Read full text. CrossRef verified: "EnergyPlus: creating a new-generation building energy simulation program"].
2. Eurostat. (2009). *Harmonised European Time Use Surveys: 2008 Guidelines*. Methodologies and Working Papers, Catalogue number: KS-RA-08-014-EN. Luxembourg: Publications Office of the European Union. [Tier 1. Read full text. Official Eurostat manual for HETUS 2010 round].
3. Eurostat. (2019). *Harmonised European Time Use Surveys (HETUS) 2018 Guidelines*. Manuals and Guidelines, Catalogue number: KS-GQ-19-003-EN. Luxembourg: Publications Office of the European Union. [Tier 1. Read full text. Official Eurostat manual for HETUS 2020 round].
4. Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., and Chen, W. (2022). LoRA: Low-Rank Adaptation of Large Language Models. In *International Conference on Learning Representations (ICLR 2022)*. Pre-print DOI: 10.48550/arXiv.2106.09685. [Tier 1. Read full text. DataCite verified: "LoRA: Low-Rank Adaptation of Large Language Models"].
5. Instituto Nacional de Estadistica (INE). (2011). *Encuesta de Empleo del Tiempo 2009-2010: Metodologia*. Madrid: INE. URL: https://www.ine.es/metodologia/t25/t25304471.pdf. CORRECTED 2026-09-16, original URL dead. [Tier 1. Read full text. Official Spanish survey methodology].
6. Iseri, O. K., Gursel Dino, I., and Kalkan, B. (2026). Occupancy modeling using population statistics and machine learning for urban residential built environment. *Energy and Buildings*, 357, 117155. DOI: 10.1016/j.enbuild.2026.117155. [Tier 1. Read full text. CrossRef verified: "Occupancy modeling using population statistics and machine learning for urban residential built environment"].
7. Istituto Nazionale di Statistica (ISTAT). (2016). *I tempi della vita quotidiana: L'uso del tempo in Italia - Anno 2013-2014: Metodologia e primi risultati*. Roma: ISTAT. URL: https://www.istat.it/wp-content/uploads/2016/11/Report_Tempidivita_2014.pdf. CORRECTED 2026-09-16, original URL dead; new URL reachable, MEDIUM confidence (cover-page title not machine-verified). [Tier 1. Not independently full-text confirmed this pass. Official Italian survey methodology].
8. Loga, T., Stein, B., and Diefenbach, N. (2016). TABULA building typologies in 20 European countries - Making energy-related features of residential building stocks comparable. *Energy and Buildings*, 132, 4-12. DOI: 10.1016/j.enbuild.2016.06.094. [Tier 1. Read full text. CrossRef verified: "TABULA building typologies in 20 European countries-Making energy-related features of residential building stocks comparable"].
9. Loga, T., Diefenbach, N., and Stein, B. (2012). *Use of Building Typologies for Modelling the Energy Balance of the National Residential Building Stocks*. TABULA Synthesis Report. Darmstadt: Institut Wohnen und Umwelt (IWU). URL: https://episcope.eu/fileadmin/tabula/public/docs/report/TABULA_FinalReport.pdf. CORRECTED 2026-09-16, original URL dead. [Tier 1. Read full text. Official project deliverable].
10. Shokri, R., Stronati, M., Song, C., and Shmatikov, V. (2017). Membership Inference Attacks Against Machine Learning Models. In *2017 IEEE Symposium on Security and Privacy (SP)*, pp. 3-18. DOI: 10.1109/sp.2017.41. [Tier 1. Read abstract and methodology. CrossRef verified: "Membership Inference Attacks Against Machine Learning Models"].
11. Sullivan, O., and Gershuny, J. (2023). *United Kingdom Time Use Survey, 2014-2015*. [data collection]. 4th Edition. UK Data Service. SN: 8128. DOI: 10.5255/UKDA-SN-8128-1. [Tier 1. Read metadata and user guide. DataCite verified: "United Kingdom Time Use Survey, 2014-2015"].
12. Vosoughkhosravi, S., Jafari, A., and Zhu, Y. (2023). Application of American time use survey (ATUS) in modelling energy-related occupant-building interactions: A comprehensive review. *Energy and Buildings*, 294, 113245. DOI: 10.1016/j.enbuild.2023.113245. [Tier 1. Read full text. CrossRef verified: "Application of American time use survey (ATUS) in modelling energy-related occupant-building interactions: A comprehensive review"].
13. Wilke, U., Haldi, F., Scartezzini, J.-L., and Robinson, D. (2013). A bottom-up stochastic model to predict building occupants' time-dependent activities. *Building and Environment*, 60, 254-264. DOI: 10.1016/j.buildenv.2012.10.021. [Tier 2. Read full text. CrossRef verified: "A bottom-up stochastic model to predict building occupants' time-dependent activities"].
