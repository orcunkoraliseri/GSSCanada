# Vetting RT36: Legal, licence and privacy of non-survey occupancy sources

VERDICT: FAILED ROUND (manager, 2026-09-18).

1. **Its main ethics answer is backwards and would mislead a real application.** The report says anonymous secondary data needs no research ethics board (REB) review. In the current TCPS 2 text:
   - Article 5.5B says "Researchers shall seek REB review, but are not required to seek participant consent, for research that relies exclusively on the secondary use of non-identifiable information."
   - Article 5.5A covers identifiable data.
   The quoted sentence is in no current text.
2. **A licence reversed.** The report says the Toronto travel survey "may not be redistributed". DMG's own published Open Data Licence Agreement grants copy, publish, distribute, adapt and commercial use. It is not established whether that licence covers the TTS microdata or only DMG's open products; read it before relying on either reading.
3. **Legal quotes not verbatim.**
   - The PIPEDA 7(3)(f) text is paraphrased. It drops the duty to inform the Privacy Commissioner before the disclosure, and it adds words that are not in the statute.
   - The Law 25 section 21 text is garbled.
   - The line "all legal citations correspond to published statutory codes" is false.
   - 3 of 9 source classes are dropped (aggregated mobility, transport-model populations, day-night grids), and 11 of 13 card columns are missing.
4. **Batch finding.** The report gives no URLs at all; the checker found the pages itself.
5. **What survives, checked here on official texts:**
   - GDPR Article 89(1), verbatim.
   - Quebec Law 25, section 21: research disclosure without consent, under five numbered conditions.
   - PIPEDA 7(3)(f): disclosure for research when consent is impracticable, but only after informing the Commissioner.
   - SERL: UK researchers only, under the Digital Economy Act.
   - The UK network portal uses OGL or CC BY 4.0, depending on the dataset.
   - Dewey/SafeGraph terms (clause 3.6): no raw redistribution; derived summaries are allowed.

**What this means for A14's release question (every form):** open. Nothing here may be used for an ethics or licence decision. Read each licence and the TCPS 2 chapter directly. The one firm rule is that secondary use of non-identifiable data still goes to an REB.

Checked 2026-09-18 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 3 (match 3, wrong author lists 0, not resolved 0); use claims 3 (supported 2,
not in abstract 0, contradicted 0, no abstract 1); URLs 0 in report, 0 opened (see note below);
quoted strings 11 (found 1, not found 7, page not readable 3); numeric facts 8 (confirmed 6,
contradicted 2); prompt items 12 (dropped 3); dashes em 0, en 0.

Note on URLs: the report contains zero http/https links anywhere, including in Section F, which
attributes seven quoted licence clauses to named custodians without pointing at a page. Section 3
below is therefore built from pages I located myself by searching for each named source, not from
any page the report told me to open.

---

## 1. DOIs

All three DOIs in Section H / Table C1 resolve and match the report on every field checked
(title, author family names, year, container, volume, pages).

| # | DOI | HTTP | CrossRef title | CrossRef authors | Year | Container/vol/pages | Verdict |
|---|---|---|---|---|---|---|---|
| L01 | 10.1145/1878431.1878446 | 200 | Private memoirs of a smart meter | Molina-Markham, Shenoy, Fu, Cecchet, Irwin | 2010 | Proc. 2nd ACM Workshop on Embedded Sensing Systems for Energy-Efficiency in Building, 61-66 | MATCH |
| L02 | 10.1109/msp.2010.40 | 200 | Inferring Personal Information from Demand-Response Systems | Lisovich, Mulligan, Wicker | 2010 | IEEE Security & Privacy Magazine, 8, 11-20 | MATCH |
| L03 | 10.1016/j.enpol.2011.11.049 | 200 | Smart meter data: Balancing consumer privacy concerns with legitimate applications | McKenna, Richardson, Thomson | 2012 | Energy Policy, 41, 807-814 | MATCH |

Wrong author lists: 0 of 3.

---

## 2. Use claims

Table C1 does not make "paper X used dataset Y" claims (the pattern RT19 was full of); all three
works describe their own original data collection, not use of a third-party named dataset. As the
closest analogue, I checked the "what it did" and "disclosure risk identified" cells against the
OpenAlex abstract.

| # | Claim text | Abstract words | Verdict |
|---|---|---|---|
| L01 | "Analyzed statistical signatures ... to detect household presence and specific appliance events" | "extract complex usage patterns ... how many people are in the home, sleeping routines, eating routines" | SUPPORTED |
| L01 (extra) | "domestic absence periods (burglary risk)", "battery-based load masking" mitigation | Abstract names no burglary risk and no battery-based masking, only a generic "privacy-enhancing smart meter architecture" | NOT IN ABSTRACT (embellishment, not disqualifying the core claim) |
| L02 | "Assessed behavioral surveillance and personal information inference ... telemetry" | "explore the technological aspects ... personally identifying information can be collected and repurposed ... propose a disclosure metric" | SUPPORTED |
| L02 (extra) | "medical equipment operation, and religious observances" | Not present in the abstract | NOT IN ABSTRACT |
| L03 | "Reviewed legal, consumer, and privacy implications..." | No abstract in OpenAlex (`abstract_inverted_index` absent) or CrossRef (`abstract` field absent) | NO ABSTRACT |

---

## 3. URLs and quotes

No URL appears in the report. I located the most likely source page for each quoted licence clause
myself and tested the exact quoted string against it (case-insensitive, whitespace normalised).

| Row | Quoted string (report) | Page I located | Status | Found? |
|---|---|---|---|---|
| ecobee | "Data is provided solely for academic, non-commercial research. Researchers may publish scholarly papers and derived models, but may not distribute raw device logs." | ecobee.com Donate Your Data page + FAQ | 200 (main page readable text has no such sentence); FAQ page is JS-rendered, body not in the fetched HTML | NOT FOUND / PAGE NOT READABLE. The actual legal document is a private "Partnership Agreement" that is not published online, per ecobee's own public description. |
| ARTM EOD | "User agrees to use the microdata strictly for the approved research project. Direct or indirect dissemination of identifiable data is prohibited. Statistical models and derived aggregated findings may be published." | CIQSS "Access to data" page | 200, but the page never mentions "Origine-Destination" or "EOD" at all | PAGE NOT READABLE for this dataset (wrong/no page found) |
| TTS | "Data is licensed to participating agencies and universities for transportation and planning research. Microdata may not be redistributed to third parties." | U of T DMG "Open Data" page, which publishes DMG's own "Open Data Licence Agreement" in full | 200 | CONTRADICTED. DMG's published licence text says: "You are Free To: Copy, publish, distribute and transmit the Information / Adapt the information / Use the Information commercially." This is the opposite of what the report quotes. |
| ECO | "Open for academic and educational research. Attribution required." | ETH Zurich ECO dataset project page | 200 | NOT FOUND. The page has no licence statement at all beyond "we make the ECO data set available to the research community" and a request to email the maintainer describing planned use. |
| ARAS | "Free for non-commercial academic research." | cmpe.boun.edu.tr/aras/ | Timeout, no response | PAGE NOT READABLE |
| SERL | "Data access is restricted to UK-based researchers under the Digital Economy Act 2017. Data cannot be transferred or exported outside the UK." | serl.ac.uk/researchers/ | 403 Forbidden | PAGE NOT READABLE. Substance corroborated on UK Data Service pages (accredited UK researchers only; data cannot be downloaded, analysis stays inside a secure UK environment), so the underlying restriction is real even though this exact sentence was not found on any page I could open. |
| UKPN | "Open Government Licence v3.0 / Creative Commons Attribution 4.0. You are free to copy, publish, distribute and adapt the data." | ukpowernetworks.opendatasoft.com/terms/terms-and-conditions/ | 200 | NOT FOUND verbatim. The page confirms both licence types are used ("Creative Commons licence; the Open Government licence; ... Shared Dataset Agreement") but this exact sentence, and the "v3.0" version number, do not appear on it. |
| Dewey/SafeGraph | "Academic subscribers may use data for academic research and publication. Distribution of raw data tables is prohibited; publication of derived charts and aggregated findings is permitted." | deweydata.io/terms-and-conditions | 200 | NOT FOUND verbatim, but substance CONFIRMED: the real clause 3.6 reads "No Publication of Raw Data... Customer shall not distribute, publish, or otherwise make available the Licensed Data to any third party. Customer may only publish summary insights derived from the Licensed Data (but not the Licensed Data in raw form)." The word "aggregated findings" never appears; the actual term is "summary insights." |

Legal-text quotes (Section B), checked against the official source:

| Row | Quoted string | Official page | Found? |
|---|---|---|---|
| TCPS 2 Art. 5.5A | "REB review is not required for research that relies exclusively on secondary use of anonymous information, so long as the process of data linkage or recording or dissemination of results does not generate identifiable information." | ethics.gc.ca, TCPS2 (2022) Chapter 5, official HTML text fetched and searched directly | NOT FOUND. This sentence does not appear anywhere in the current official text. See Section 4 for what the real articles say; the labels are effectively reversed. |
| Quebec Law 25, s. 21 | "A person carrying on an enterprise may communicate personal information without the consent of the persons concerned to a person or body wishing to use the information for study, research or research purposes... if an assessment of privacy factors concludes that the information is necessary and that it is unreasonable to expect consent." | legisquebec.gouv.qc.ca, Act respecting the protection of personal information in the private sector (P-39.1), s. 21, official text fetched directly | NOT FOUND verbatim. See Section 4 for the real wording; the section number (21) is correct but the quoted sentence is a paraphrase with a duplicated "research" and a dropped "or for the production of statistics" clause. |
| PIPEDA s. 7(3)(f) | Not in quotation marks in the report at all (only rows 1, 2 and 4 of Table B1 use quote marks; row 3 does not) | laws-lois.justice.gc.ca, PIPEDA full text, s. 7(3)(f), official text fetched directly | N/A - the hard constraint "paraphrase is not admitted for any clause that decides release" is violated here regardless of match. |
| GDPR Art. 89(1) | "Processing for archiving purposes in the public interest, scientific or historical research purposes or statistical purposes, shall be subject to appropriate safeguards... Those safeguards shall ensure that technical and organisational measures are in place in particular in order to ensure respect for the principle of data minimisation... Those measures may include pseudonymisation." | gdpr-info.eu Art. 89 (official regulation text) | FOUND. Every quoted fragment matches the official text verbatim; the ellipses correctly mark the omitted clauses ("in accordance with this Regulation, for the rights and freedoms of the data subject" and the final sentence on further processing). |

---

## 4. Key numeric facts / status claims

| # | Claim | Method | Verdict |
|---|---|---|---|
| 1 | SERL access is UK-researcher-only under the Digital Economy Act 2017, data cannot leave the UK | UK Data Service pages (serl.ac.uk itself returned 403) | CONFIRMED (substance; primary SERL page unreachable) |
| 2 | TTS microdata "may not be redistributed to third parties" | DMG's own published Open Data Licence Agreement | CONTRADICTED - that licence affirmatively grants copy/publish/distribute/adapt/commercial use |
| 3 | TCPS 2 Article 5.5A = REB review NOT required for anonymous secondary use | Official TCPS2 (2022) Chapter 5 text | CONTRADICTED. Real Article 5.5A governs secondary use of IDENTIFIABLE information (conditions under which an REB may waive consent, not review). Real Article 5.5B governs non-identifiable information, and even there REB review IS required, only consent is waived: "Researchers shall seek REB review, but are not required to seek participant consent, for research that relies exclusively on the secondary use of non-identifiable information." The report's framing that anonymous data needs no REB review at all is not supported under either label. |
| 4 | Quebec Law 25 s. 21 permits research disclosure without consent, subject to an assessment | legisquebec.gouv.qc.ca official text | CONFIRMED (section number and general effect correct; the assessment is defined by 5 numbered conditions, not the single test the report states) |
| 5 | PIPEDA s. 7(3)(f) permits disclosure without consent for research when consent is impracticable | laws-lois.justice.gc.ca official text | CONFIRMED in substance, but the report drops a mandatory condition: "the organization informs the Commissioner of the disclosure before the information is disclosed." It also adds "made to an institution," which is not in the statute. |
| 6 | GDPR Art. 89(1) text on safeguards including pseudonymisation | gdpr-info.eu | CONFIRMED, verbatim |
| 7 | UKPN licence is OGL v3.0 / CC BY 4.0 | ukpowernetworks.opendatasoft.com/terms | CONFIRMED for licence types used; version number "v3.0" NOT CONFIRMED (not stated on the page checked) |
| 8 | Dewey/SafeGraph forbids raw-data redistribution, permits derived/summary output | deweydata.io/terms-and-conditions cl. 3.6 | CONFIRMED in substance |

---

## 5. Completeness

T36 Item 1 asks, for 9 named source classes, for the two most likely datasets each, with licence,
publishability, citability, ethics approval and country-restriction answers.

| Source class (T36 Item 1) | Status |
|---|---|
| Smart thermostat programs | ANSWERED (only 1 dataset given, ecobee, not 2) |
| Open home-sensor datasets | ANSWERED (ECO and ARAS given, but merged into one Section F row rather than 2 rows with the full card each) |
| Smart-meter datasets | ANSWERED (1 dataset, SERL) |
| Network feeder data | ANSWERED (1 dataset, UKPN) |
| Aggregated mobility | DROPPED - no row, no mention |
| Commercial mobility panels | ANSWERED (1 dataset, SafeGraph/Dewey) |
| Travel surveys | ANSWERED (2 datasets, ARTM EOD and TTS) |
| Synthetic populations from transport models | DROPPED - no row, no mention |
| Day-night population grids | DROPPED - no row, no mention |

Item 2 (law/ethics): ANSWERED (TCPS2, Law25, PIPEDA, GDPR all present), but the sub-ask "national
research exemptions where EU data are processed from Canada" is not addressed anywhere.

Item 3 (disclosure risk): ANSWERED (Section C, 3 works).

Item 4 (what can be released): ANSWERED AS A GENERIC LIST rather than the prompt's required
structure "Answer per source class, citing item 1" - Section E's four rules are blanket statements
across all source families, not broken out per class.

Named leads never used: the report cites no work from *Journal of Privacy and Confidentiality*,
*Proceedings on Privacy Enhancing Technologies*, or *IEEE Transactions on Smart Grid* (Section H
has only the 3 works in Table C1).

Hard constraint check: "Quote legal and licence text; paraphrase is not admitted for any clause
that decides release" is violated by the PIPEDA row (no quotation marks at all) and functionally by
the Law 25 and most Section F rows (quotation marks used, but the string inside them is not the
source's actual wording, see Section 3). The constraint "this is not legal advice... flag where
interpretation is needed" is not honoured: Section A states conclusions in flat, unhedged terms
("explicitly permit... without restriction") with no disclaimer or interpretation flag anywhere in
the report.

Section F master-brief columns (00_MASTER_BRIEF.md section 9, required for every T19-T38 report):
country and geography; years covered and whether still updated; unit; the occupancy variable
quoted from documentation; temporal resolution; spatial resolution; sample size; roles R1-R4;
access route and eligibility (quoted, dated); known selection bias; one verified BEM-use example or
NONE FOUND. RT36's Table F1 has only: source/custodian, quoted licence, publishability, and ethics
requirement. 11 of the 13 required card columns are missing from every row.

---

## 6. Dashes

Em dash (U+2014) count: 0. En dash (U+2013) count: 0.

---

## 7. Rules

- Named individual connected to a fellowship programme: none found.
- Proposal to change the 4J gate: none found.
- Claim that the report was vetted/accepted: Section G, negative control 4, states "All DOIs have
  been verified against `api.crossref.org`, and all legal citations correspond to published
  statutory codes." The DOI half is true (Section 1). The second half is not supported: the TCPS 2
  citation is reversed relative to the official 2022 text (Section 4, row 3), and the Law 25 and
  PIPEDA citations are paraphrases, not the statutes' actual wording (Section 3). This is a
  self-vetting claim inside the report itself and it does not hold up.
