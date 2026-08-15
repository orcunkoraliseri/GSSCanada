# RL20. Is the Norwegian Time-Use File Admissible to Our Corpus, or Not?

## Section A. Direct answer

The Norwegian time-use survey file obtainable through national channels is inadmissible to our four-country HETUS training corpus because it does not carry Eurostat Activity Coding List (ACL) codes and no official recode table exists. The microdata file distributed to researchers by Sikt (formerly NSD) under study NSD1849 carries only Statistics Norway's (SSB) proprietary national classification of 167 activity categories, derived historically from the 1965 Szalai multinational pilot rather than Eurostat ACL 2008. No ACL-coded activity variable is delivered in the Sikt download, and neither Statistics Norway nor Sikt publishes a documented one-to-one correspondence table to ACL 2008. Admitting Norway would therefore require constructing a bespoke, unauditable crosswalk across heterogeneous activity definitions, violating the project's explicit methodology constraints. Furthermore, Statistics Norway truncates its survey universe to ages 9 to 79, entirely excluding elderly individuals aged 80 and older, which introduces an unbridgeable structural demographic mismatch against our four base countries (UK, Spain, France, Italy) for residential building energy simulations. Consequently, the Norwegian file must be rejected, and the paper's core design must remain anchored on the four established HETUS waves.

---

## Section B. Findings table

| # | Finding | Value or statement | Type (fact / inference) | Source | Tier | Date checked | Confidence (H/M/L) |
|---|---|---|---|---|---|---|---|
| B1 | Activity coding list in delivered Sikt file | Sikt study NSD1849 delivers activity variables coded strictly in SSB's proprietary 167-category national classification; no Eurostat ACL variable is present. | Fact | Sikt Surveybanken NSD1849 Study Record and Variable Documentation [R1, R2] | Tier 1 | 2026-08-14 | H |
| B2 | Existence of official SSB to ACL recode table | NOT FOUND. Neither Statistics Norway nor Sikt publishes an official, citable correspondence table mapping the 167 national codes to Eurostat ACL 2008 3-digit categories. | Fact | Review of SSB Notater 2012/03 and Sikt metadata [R2, R3] | Tier 1 | 2026-08-14 | H |
| B3 | Historical origin of SSB 167-category classification | SSB's 167 activity categories are structured into 5 main groups, originating from the 1965 Szalai multinational time-budget study and adapted by SSB across waves since 1971. | Fact | SSB Time Use Survey Documentation and Klass Standard [R3, R4] | Tier 1 | 2026-08-14 | H |
| B4 | Correct technical documentation report for 2010 survey | The definitive methodology and data quality report is Holmøy, Lillegård and Löfgren (2012), SSB Notater 2012/03 (not Vaage 2012 Rapporter 2012/36). | Fact | Statistics Norway Official Publications Archive [R3] | Tier 1 | 2026-08-14 | H |
| B5 | Character of Vaage (2012) publication | Vaage (2012), "Tidene skifter: Tidsbruk 1971-2010", is published as Statistiske analyser 125 (SA 125), containing substantive trend analysis rather than technical survey documentation. | Fact | Statistics Norway SA 125 [R5] | Tier 1 | 2026-08-14 | H |
| B6 | Sikt Surveybanken study identifiers and DOIs | Sikt catalogue indexes the 2010 survey under study identifier NSD1849, with interview file DOI 10.18712/NSD-NSD1849-2-V3 and linked diary component. | Fact | Sikt Surveybanken Archive [R1] | Tier 1 | 2026-08-14 | H |
| B7 | Survey sample age truncation | The Norwegian 2010 survey samples gross population aged 9 to 79 only; persons aged 80 and older are excluded from the sampling frame. | Fact | SSB Notater 2012/03, Section 2.1 [R3] | Tier 1 | 2026-08-14 | H |
| B8 | Diary structure and sampling resolution | 10-minute diary intervals (144 slots/day), 2 diary days per respondent (1 weekday, 1 weekend day), paper diary collection. | Fact | SSB Notater 2012/03, Section 1.2 [R3] | Tier 1 | 2026-08-14 | H |
| B9 | Sikt microdata licence on synthetic data | Sikt standard end-user agreements and Norwegian data protection terms are completely silent regarding synthetic data and generative AI outputs. | Fact | Sikt Research Data Terms of Use [R6] | Tier 1 | 2026-08-14 | H |
| B10 | Sikt terms on multi-country data pooling | Sikt permits statistical processing and model training on approved research projects, but forbids re-identifying data linkage with external administrative registries. | Fact | Sikt Standard Data Agreement [R6] | Tier 1 | 2026-08-14 | H |
| B11 | HETUS 2010 round alternative national routes | Outside the four base countries (FR, IT, ES, UK), no participating country distributes an official ACL 2008-coded microdata file via an unencumbered Tier 0 to Tier 3 route. | Fact | Cross-national NSI and archive review in RL19 [R7] | Tier 1 | 2026-08-14 | H |

---

## Section C. Decision impact

| Decision this bears on | What we currently plan | What the evidence says | Change required: none / caveat / design change / stop | Effort |
|---|---|---|---|---|
| Admissibility of Norway to 4-country corpus | Evaluate admitting Norway as a 5th country to expand source training folds from 3 to 4. | Sikt ships only SSB's 167-category classification without Eurostat ACL codes or an official recode table. Norway also truncates ages 80+. | Stop: Do not admit Norway. Maintain the 4-country corpus (IT, ES, UK, FR). | None (saves compute and engineering effort) |
| Harmonisation pipeline engineering | Build a universal HETUS ingestion parser assuming all acquired files share ACL 2008. | National archives distribute idiosyncratic classifications (SSB 167 codes in Norway, ZVE 165 codes in Germany). | Caveat: Confine the unified ETL parser strictly to the four validated HETUS SUF/national files (IT, ES, UK, FR). | Low |
| Substantive handling of Nordic archetype | Claim cross-European generalisability including Nordic residential regimes. | Nordic microdata cannot be harmonised without bespoke, unauditable crosswalks or Eurostat SUF Track A access. | Caveat: Explicitly scope the paper's empirical claims to Western and Southern European HETUS regimes. | Low |

---

## Section D. Feasibility on our hardware and licences

| Item | Requirement | Do we meet it on a shared single-node SLURM GPU? | If not, the cheapest thing that would |
|---|---|---|---|
| Retaining 4-country core corpus | Training 4 leave-one-country-out folds on Concordia Speed HPC. | Yes. Fully supported within standard GPU memory and 7-day walltime limits. | N/A |
| Rejection of bespoke crosswalk | Eliminating unauditable 167-to-ACL2008 translation tables from training pipeline. | Yes. Reduces pipeline complexity and eliminates data distortion risks. | N/A |
| Synthetic data compliance | Generating CC BY 4.0 synthetic diaries from models trained on approved base files. | Yes. Fully compliant with project release policies. | N/A |

---

## Section E. What this changes in the write-up

* [Tied to B1, B2, B3] The data section must explicitly report that national statistical releases of HETUS-participating countries (such as Norway's Tidsbruksundersøkelsen 2010 via Sikt) frequently retain legacy national classifications (SSB 167 categories) rather than Eurostat ACL 2008, preventing automated cross-national ingestion.
* [Tied to B4, B5] Any citation to Norwegian time-use documentation must cite Holmøy, Lillegård and Löfgren (2012, SSB Notater 2012/03) for survey methodology and sampling, correcting the inaccurate citation of Vaage (2012, Rapporter 2012/36).
* [Tied to B7] The methodology and discussion sections should note the demographic sampling boundaries of national surveys: Norway truncates respondents aged 80 and above, whereas our four core HETUS countries capture the complete adult and elderly age distribution essential for residential occupancy profiling.
* [Tied to B11] The discussion of multi-country corpus construction must document that national dissemination routes outside the four base countries do not provide plug-and-play ACL-coded microdata, justifying why centralized Eurostat SUF access or a tightly controlled four-country core is required.

---

## Section F. Concrete artefacts to retrieve

| Artefact | What it is | Direct URL to a file or to a landing record with a download control | Access condition (open / registration / application / paywalled) | Confirmed reachable? |
|---|---|---|---|---|
| SSB Notater 2012/03 PDF | Official documentation report for Norwegian Time Use Survey 2010 | `http://www.ssb.no/a/publikasjoner/pdf/notat_201203/notat_201203.pdf` | Open access direct download | Yes |
| SSB SA 125 PDF | Substantive trend analysis report (Vaage 2012) | `https://www.ssb.no/a/publikasjoner/pdf/sa125/sa125.pdf` | Open access direct download | Yes |
| Sikt NSD1849 Catalogue Landing Record | Sikt Surveybanken study record for Tidsbruksundersøkelsen 2010 | `https://surveybanken.sikt.no/en/study/NSD1849` | Registration (Tier 2 academic login) | Yes |
| Sikt NSD1849-2 Persistent DOI | Persistent identifier for Norwegian interview microdata | `https://doi.org/10.18712/NSD-NSD1849-2-V3` | Registration (Tier 2 academic login) | Yes |

---

# PART A: THE DECIDING FACT

## A1. What the Delivery Actually Contains

| # | Question | Finding / Value | Source Document |
|---|---|---|---|
| A1.1 | Is there a variable in the delivered file holding the activity in Eurostat ACL codes? | **No.** The delivered diary dataset contains only national activity variables (`akt1` to `akt144` / `hovedaktivitet`) coded in SSB's 167-category classification. No ACL variable (2-digit or 3-digit) is provided. | Sikt Surveybanken NSD1849 Variable List [R1]; SSB Notater 2012/03 [R3] |
| A1.2 | If yes, who produced it (SSB, Eurostat, archive, researcher)? | **N/A.** No ACL-coded variable is delivered in the research file. (SSB generated internal harmonised files for Eurostat's central database, but these are not delivered through Sikt). | Sikt Study Metadata [R1]; Eurostat HETUS 2010 Overview [R7] |
| A1.3 | Which edition of the ACL (1997/2000, 2008, 2010, 2020)? | **N/A.** None delivered in the national release. | Sikt NSD1849 Documentation [R1] |
| A1.4 | Is there a published recode or correspondence table between the Norwegian national list and the ACL? | **NOT FOUND.** No official, published recode table mapping SSB 167 categories to Eurostat ACL 2008 exists in SSB documentation, Sikt metadata, or official reports. | Comprehensive search of SSB publications and Klass database [R2, R3, R4] |
| A1.5 | How many categories does the national list actually have, and at what depth is it released? | **Exactly 167 categories**, released at full 3-digit national integer code depth (grouped under 5 main activity domains). | SSB Notater 2012/03 [R3]; SSB Klassifikasjoner [R4] |

## A2. Where the Answer Came From

* **A1.1:** Verified directly from Sikt Surveybanken study record NSD1849 variable catalogue and SSB Notater 2012/03.
* **A1.2:** Sikt archive documentation and Eurostat microdata dissemination documentation.
* **A1.3:** Sikt archive documentation.
* **A1.4:** Exhaustive review of SSB Notater 2012/03, Vaage (2012), SSB Klass system, and Sikt study documentation. (Result: `NOT FOUND`).
* **A1.5:** SSB Notater 2012/03, Section 1.2 and Appendix, corroborated by SSB Klass standard for time-use surveys.

---

# PART B: THE ROUTE (SKIPPED PER PROTOCOL)

*As mandated by prompt instructions: Because A1.1 is negative (no Eurostat ACL variable is delivered in the obtainable file), Part B is skipped entirely.*

---

# PART C: THE LICENCE QUESTION THAT DOES NOT TRANSFER

## C1. Synthetic Data Generation and Publication

* **Finding:** The Sikt / Statistics Norway standard data user agreement is **silent** regarding generative AI models, synthetic data generation, and the publication of synthetic time-use diaries.
* **Relevant Clauses:** Sikt terms govern the confidentiality of individual respondents, prohibiting any attempt to identify natural persons or redistribute primary unit-level microdata. They require data to be stored securely and deleted or archived according to project duration.
* **Assessment:** Silence is not an explicit permission. However, because synthetic diaries produced by a generative model contain no 1-to-1 mapping to real individuals and prevent re-identification, releasing synthetic microdata under CC BY 4.0 complies with standard statistical disclosure control principles, provided no primary records or model weights are published.

## C2. Combining Microdata in Multi-Country Training

* **Finding:** Sikt standard terms permit combining data from different sources for the purpose of statistical modeling within the approved research project, provided that dataset merging does not aim to re-identify individuals through direct record linkage with administrative population registers.
* **Assessment:** Pooling Norwegian microdata with other European national datasets into an anonymised training matrix is legally permitted under Sikt research terms.

---

# PART D: THE JUDGEMENT

## D1. Admissibility Without a Hand-Built Crosswalk

**No.**
The obtainable Norwegian file from Sikt contains only SSB's proprietary 167-category classification. Without an official ACL variable or an official SSB recode table, admitting Norway would require constructing a manual, ad-hoc crosswalk to Eurostat ACL 2008. Under the project's strict methodological constraints (established in RL17 B3), arbitrary one-to-many mappings cannot be defended across heterogeneous surveys and would corrupt the appliance-triggering activity representations.

## D2. Status of Published Third-Party Crosswalks

**NOT FOUND.**
No published, citable, peer-reviewed correspondence table mapping SSB's 167 categories to Eurostat ACL 2008 exists in the academic literature. While the Multinational Time Use Study (MTUS) harmonises Norwegian data into the 69-category or 41-category MTUS classification (e.g. Fisher & Gershuny, CTUR), MTUS harmonisations collapse activity detail below the granularity required for building energy simulation and do not map to the 3-digit Eurostat ACL 2008 standard.

## D3. Counter-Examples Across HETUS 2010 Round

**None.**
Outside our four established base countries (Spain at Tier 0, UK at Tier 2, France at Tier 2, Italy at Tier 2/3), no participating country in the HETUS 2010 round distributes an official ACL 2008-coded file via an unencumbered national route (Tier 0 to Tier 3). Germany (FDZ) uses national ZVE codes (165 categories); the Netherlands (DANS) uses a non-standard 7-day diary; Belgium and Austria require Tier 4 institutional pre-accreditation; and Finland and Hungary restrict access strictly to Tier 5 secure on-site or remote enclaves.

---

# PART E: THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

### The Decisive Flaw: Age Truncation at 79 and Exclusion of Elderly Occupants

The single most critical structural flaw in admitting Norway specifically is **sampling frame age truncation**:

* **Evidence:** Statistics Norway's Tidsbruksundersøkelsen 2010 sampled persons aged **9 to 79 only** (Holmøy, Lillegård & Löfgren, 2012, Section 2.1, p. 7). Individuals aged **80 years and older were systematically excluded** from the survey sample.
* **Impact on UBEM/BEM:** In building energy modeling, non-working elderly occupants (especially individuals aged 80+) exhibit the highest continuous residential presence, the highest daytime heating requirements, and the most distinctive domestic appliance usage patterns in cold-climate high-latitude winter regimes.
* **Mismatch Against Base Corpus:** In contrast to Norway, our four core HETUS countries (UK, Spain, France, Italy) sample the full adult and elderly population without an upper age ceiling (or up to 90+). Admitting Norway would inject a structural demographic truncation that causes leave-one-country-out demographic reweighting to fail whenever evaluating the energy impact of elderly populations.
* **Cheapest Document to Confirm:** **SSB Notater 2012/03**, Section 2.1 (*Utvalg og populasjon*, p. 7), available as a free open-access PDF directly from Statistics Norway (`http://www.ssb.no/a/publikasjoner/pdf/notat_201203/notat_201203.pdf`).

---

## Section G. Contradictions, gaps, open questions, and mandatory negative controls

### Vetted Corrections to Previous Reports

* **Documentation Report Citation Error:** `RL19` cited Vaage (2012), *Rapporter 2012/36*. This citation was erroneous. The correct technical documentation report for the 2010-2011 survey is **Holmøy, Lillegård and Löfgren (2012), Notater 2012/03**. Vaage (2012) is *Tidene skifter: Tidsbruk 1971-2010*, published as *Statistiske analyser 125 (SA 125)*.
* **Refutation of Documented One-to-One Recode Table:** `RL19` asserted that a documented one-to-one recode table between SSB codes and Eurostat ACL 2008 was supplied. Thorough examination of SSB and Sikt documentation reveals this assertion is unsupported. No such table exists in the public or academic distribution.
* **Catalogue Identifier and URL:** Sikt Surveybanken addresses study records by persistent DOI (`10.18712/NSD-NSD1849-2-V3`) and study ID `NSD1849` (`https://surveybanken.sikt.no/en/study/NSD1849`).

### Mandatory Negative Controls

1. **List of documents opened in full, with URLs:**
   * *Statistics Norway (SSB) primary documents:*
     * Holmøy, A., Lillegård, M. og Löfgren, T. (2012): *Tidsbruksundersøkelsen 2010. Dokumentasjon av datainnsamling, analyse av datakvalitet og beregning av frafallsvekter*. Notater 2012/03. URL: `http://www.ssb.no/a/publikasjoner/pdf/notat_201203/notat_201203.pdf` (Opened in full).
     * Vaage, O. (2012): *Tidene skifter. Tidsbruk 1971-2010*. Statistiske analyser 125 (SA 125). URL: `https://www.ssb.no/a/publikasjoner/pdf/sa125/sa125.pdf` (Opened in full).
     * SSB Klassifikasjoner og kodelister: *Standard for tidsbruksundersøkelser*. URL: `https://www.ssb.no/klass/` (Opened in full).
   * *Archive catalogue records:*
     * Sikt Surveybanken: Study Record `NSD1849` / DOI `10.18712/NSD-NSD1849-2-V3`, *Tidsbruksundersøkelsen 2010*. URL: `https://surveybanken.sikt.no/en/study/NSD1849` (Opened in full).
   * *Third-party and institutional standards:*
     * Eurostat (2009): *Harmonised European Time Use Surveys: 2008 Guidelines*. Methodologies and Working Papers. Luxembourg: Publications Office of the European Union (Opened in full).

2. **Eurostat aggregate table vs national archive microdata:**
   * At no point did we conclude Norway uses HETUS guidelines merely because Norway appears in Eurostat aggregate tables. Appearing in Eurostat tables indicates that Statistics Norway prepared an internal data transmission for Eurostat; it does not indicate what Sikt delivers to researchers. Sikt delivers the national file in SSB's 167-category format.

3. **Count of convenient findings:**
   * Across the six critical axes (obtainable, cheap, fast, ACL-coded, official recode exists, licence permits release of generated data):
     * Obtainable: Convenient (Yes, Tier 2).
     * Cheap: Convenient (NOK 0 / EUR 0).
     * Fast: Convenient (1 to 3 days).
     * ACL-coded: **Inconvenient / Negative (No, 167 national codes only).**
     * Official recode exists: **Inconvenient / Negative (NOT FOUND / No).**
     * Licence permits release of generated data: **Inconvenient / Neutral (Silent, not explicit).**
   * *Summary:* Exactly 3 of 6 axes came back logistically convenient, but **0 of the 2 deciding technical admissibility criteria (ACL-coded, official recode)** were satisfied. The negative technical findings are decisive.

4. **Recode table existence:**
   * We found **neither the recode table itself nor an official statement from Statistics Norway that one is published for external users**. RL19's prior statement was unverified and is formally retracted.

5. **Impact of recode non-existence on recommendation:**
   * Our negative recommendation is strictly determined by the absence of an official ACL variable and the absence of a published, authoritative recode table. Were an official 1-to-1 recode table published by Statistics Norway, Norway would be technically harmonisable, though still subject to the age truncation limitation (ages 9-79).

---

## Section H. Full reference list

1. Sikt - Norwegian Agency for Shared Services in Education and Research (2012). *Tidsbruksundersøkelsen 2010 [Time Use Survey 2010]* (Study record NSD1849, Version 3). DOI: `https://doi.org/10.18712/NSD-NSD1849-2-V3`. Tier 1. Read catalogue metadata and documentation.
2. Sikt Surveybanken (2026). *Catalogue Record: Tidsbruksundersøkelsen 2010 (NSD1849)*. URL: `https://surveybanken.sikt.no/en/study/NSD1849`. Tier 1. Read study overview and variable lists. Checked: 2026-08-14.
3. Holmøy, A., Lillegård, M., & Löfgren, T. (2012). *Tidsbruksundersøkelsen 2010: Dokumentasjon av datainnsamling, analyse av datakvalitet og beregning av frafallsvekter [Time Use Survey 2010: Documentation of data collection, data quality analysis and non-response weight calculation]*. Notater 2012/03. Statistisk sentralbyrå (Statistics Norway), Oslo-Kongsvinger. URL: `http://www.ssb.no/a/publikasjoner/pdf/notat_201203/notat_201203.pdf`. Tier 1. Read full text.
4. Statistisk sentralbyrå (2026). *Klass: Klassifikasjoner og kodelister - Tidsbruksundersøkelsen*. Statistics Norway Classification Database. URL: `https://www.ssb.no/klass/`. Tier 1. Read full classification structure. Checked: 2026-08-14.
5. Vaage, O. F. (2012). *Tidene skifter: Tidsbruk 1971-2010 [Times are changing: Time use 1971-2010]*. Statistiske analyser 125 (SA 125). Statistisk sentralbyrå (Statistics Norway), Oslo-Kongsvinger. URL: `https://www.ssb.no/a/publikasjoner/pdf/sa125/sa125.pdf`. Tier 1. Read full text.
6. Sikt (2026). *Generelle avtalevilkår for forskningsdata og Surveybanken [Standard terms of use for research data and Surveybanken]*. URL: `https://sikt.no/avtaler-og-vilkar`. Tier 1. Read standard terms. Checked: 2026-08-14.
7. RL19 (2026). *Can the Corpus Be Widened Past Four Countries Without a Eurostat Licence?* Deep Research Series, 4J Project. Tier 1 internal benchmark. Read full text.
8. Iseri, O., Gursel Dino, I., & Kalkan, K. (2026). *Occupancy modeling using population statistics and machine learning for urban residential built environment*. Energy and Buildings, 357, 117155. DOI: `https://doi.org/10.1016/j.enbuild.2026.117155`. CrossRef verified title: "Occupancy modeling using population statistics and machine learning for urban residential built environment". Tier 2. Read full text.
