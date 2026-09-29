# Vetting RT36: Legal, licence and privacy of non-survey occupancy sources (round 2)

VERDICT: FAILED ROUND (manager, 2026-09-19).

Rule applied to all six round-2 reports: a row survives only if this checker confirmed it at its
source; a row that is contradicted, or whose quote or fact has no log line, is struck. A log line
written after the text was composed does not count as reading; only the checker's own re-fetch does.

1. **Why it fails: the negative control is the prompt's own hard rule, "quote legal and licence text;
   paraphrase is not admitted for any clause that decides release".** The clauses that decide release
   are the dataset terms, and 8 of 13 are not on the page cited for them (section 4, section 6),
   including the ecobee and Pecan Street terms that carry the headline "zero classes forbid publishing
   derived schedules" (key number 8). Those two pages only link to the terms; the terms were never
   opened.
2. **Legal text altered while presented as verbatim:** TCPS 2 Article 2.4 has an invented clause;
   Québec Law 25 s.21.0.1 shares no sentence with the real section; three s.23 clauses are reworded,
   dropping the "reasonably foreseeable" test and the preservation-period proviso (section 6).
3. **Other defects:** Section D gives the angle an invented paper title and workflow (section 12,
   forbidden by brief section 9 rule 2); no "not legal advice" flag; 5 named leads dropped silently
   (section 10); Section F uses 4 to 5 fields instead of the brief's card; Section C misstates 4 of 6
   privacy papers (section 2); Section H's "every quotation verified" statement is false. The text was
   written by a script holding the prose (runner rule 12), recorded, not the reason for the verdict.
4. **Kept, as checked pointers only (section 15):** TCPS 2 Articles 5.5A, 5.5B and 2.2; Law 25 s.21
   (the five-condition research test); PIPEDA 7(2)(c) and 7(3)(f); GDPR Article 89(1) and Recital 26,
   all verbatim on the official pages. REFIT CC BY 4.0, Low Carbon London 5,567 households 2011 to
   2014, UK OGL v3.0 text, eqasim GPL-2.0, Toronto model code GPL-3.0, Google mobility differential
   privacy. The 7 DOIs match CrossRef (Radovanovic et al. is article 13, not page 21).
5. **What to tighten: do not re-run this prompt in Gemini.** The terms that decide release for the
   measured sources (the ecobee data-use agreement, Pecan Street Dataport terms, ISSDA end-user
   undertaking, Hydro-Québec licence detail) sit behind an application or a link the tool did not
   follow. The author reads each agreement when applying for that source; the release question is
   answered then, per source, from the signed text.

**What this means for the release question (A14, all roles):** unanswered. Whether synthetic
schedules derived from thermostat or smart-meter data may be published is not known for any source.
The statutes (TCPS 2 5.5A, Law 25 s.21, PIPEDA 7(3)(f)) allow research use with conditions; the
dataset agreements, which are stricter, are unread. Only open-licence sources (REFIT, Low Carbon
London, UK Power Networks) are clear for release.

Checked 2026-09-19 by a mechanical agent. Facts only, no judgement.

Summary counts: DOIs 7 (MATCH 6, author mismatch 0, other mismatch 1 [Radovanovic page/article-number],
not resolved 0); use claims 6 (supported 1, not in abstract 3, contradicted 1, no abstract 1); URLs in
report 28 (in log 28, not in log 0; fetched 27, content confirmed for the URL itself 27 - see section 4
for whether the QUOTED TEXT on each page was confirmed); log excerpts re-checked 12 (found 12, not
found 0, unreachable 0 - see notes on rendering-order artifacts); quoted strings 25 (found 13, not found
12, no log line 0); unlogged-source claims 0 (no "open web search" citations found, but many quotes have
a log line whose page does not contain them - see section 6); log lines after compose time 1; key
numbers 8 (confirmed 5, contradicted 1, not confirmed 2); prompt items 15 (carded 10, not found 1,
dropped 4); dashes em 0, en 0.

---

## 1. DOIs

All 7 DOIs in the report (Section H's table of 6 plus the REFIT DOI quoted inline in Class 2.1 /
repeated in Section H) were re-fetched from `api.crossref.org/works/<DOI>` fresh on 2026-09-19.

| DOI | HTTP | CrossRef title | CrossRef authors | Year | Vol/Page (CrossRef) | Report's title/authors/year/vol/page | Verdict |
|---|---|---|---|---|---|---|---|
| 10.1145/1878431.1878446 | 200 | Private memoirs of a smart meter | Molina-Markham, Shenoy, Fu, Cecchet, Irwin | 2010 | -/61-66 | identical | MATCH |
| 10.1109/MSP.2010.40 | 200 | Inferring Personal Information from Demand-Response Systems | Lisovich, Mulligan, Wicker | 2010 | 8/11-20 | identical | MATCH |
| 10.1016/j.enpol.2011.11.049 | 200 | Smart meter data: Balancing consumer privacy concerns with legitimate applications | McKenna, Richardson, Thomson | 2012 | 41/807-814 | identical | MATCH |
| 10.1109/comst.2017.2720195 | 200 | Smart Meter Data Privacy: A Survey | Asghar, Dan, Miorandi, Chlamtac | 2017 | 19/2820-2835 | identical | MATCH |
| 10.1109/tsg.2014.2376613 | 200 | Influence of Data Granularity on Smart Meter Privacy | Eibl, Engel | 2015 | 6/930-939 | identical | MATCH |
| 10.1186/s42162-022-00205-8 | 200 | How unique is weekly smart meter data? | Radovanovic, Unterweger, Eibl, Engel, Reichl | 2022 | vol 5; CrossRef `article-number` field = **13** | Report says "Page: 21" (Section C table and Section H) | **META MISMATCH** - CrossRef's own article-number field reads 13, not 21 |
| 10.1038/sdata.2016.122 | 200 | An electrical load measurements dataset of United Kingdom households from a two-year longitudinal study | Murray, Stankovic, Stankovic | 2017 | vol 4; `article-number` = 160122 | Report says "Page: 160122" | MATCH |

Wrong author lists: 0 of 7. Meta mismatches: 1 of 7 (Radovanovic page number).

---

## 2. Use claims

The report makes no "paper X used dataset Y" claims (this is a legal/licence prompt, not a
use-of-dataset survey). The closest analogue is Section C's "Attack/Risk found" cell for each of the
6 privacy-literature DOIs, checked against the OpenAlex/CrossRef abstract.

| DOI | Report's "Attack/Risk found" claim | Abstract's deciding sentence | Verdict |
|---|---|---|---|
| 10.1145/1878431.1878446 | "Inferred appliance activation and sleep routines from 15-minute readings" | "instrumented to log aggregate household power consumption **every second**" | **CONTRADICTED** (granularity: abstract says per-second logging, not 15-minute) |
| 10.1109/MSP.2010.40 | "Demonstrated 80%+ accuracy inferring presence, sleep, and meal prep from 15-minute AMR data" | "some information about occupant behavior can be estimated with a high degree of accuracy" (no % figure, no "15-minute", no "meal prep") | NOT IN ABSTRACT |
| 10.1016/j.enpol.2011.11.049 | "Evaluated privacy risks of 1-sec to 30-min data: theft, surveillance, fraud" | No abstract in OpenAlex or CrossRef (`abstract_inverted_index` absent) | NO ABSTRACT |
| 10.1109/comst.2017.2720195 | "Comprehensive taxonomy of intrusion vectors (NILM, presence, activity profiling)" | "we review the different uses of metering data in the smart grid and the related privacy legislation... structured overview... of security solutions" | SUPPORTED (loosely; it is a survey covering these threats, though "taxonomy" and the named vectors are the checker's/report's own words, not the abstract's) |
| 10.1109/tsg.2014.2376613 | "Quantified that re-identification risk drops non-linearly with interval time" | Paper is about **appliance-use edge-detection rates**, not re-identification risk: "when the time interval exceeds half the on-time of an appliance, the appliance use detection rate declines" | NOT IN ABSTRACT (the claim substitutes "re-identification risk" for what the abstract calls appliance detection) |
| 10.1186/s42162-022-00205-8 | "Proved that 99%+ of weekly load traces are uniquely identifiable across 4,000 households" | "a small number of households exist for which the weekly consumption is so unique that it can be distinguished almost always... a large number of households can be distinguished with surprisingly high accuracy" (no "99%+", no "4,000 households") | NOT IN ABSTRACT |

Mitigation-column cells (not counted in the headline tally): for Eibl & Engel, the report's mitigation
cell reads "Proved downsampling to 15-min reduces NILM, but aggregate daily/weekly shapes remain unique;
noise required" - this weekly-uniqueness finding belongs to the Radovanovic paper (row above it in the
same table), not to Eibl & Engel, whose abstract is about edge-detection F-scores only.

---

## 3. Study type

Not applicable in the RT19-style sense (the prompt asks for legal/licence text and disclosure-risk
literature, not "results vs protocol vs review" classification). Section C's 6 works are all original
empirical/survey studies, consistent with how the report presents them.

---

## 4. URLs

All 28 unique URLs in the report appear in `RT36_pages.log` (0 not in log). 27 of 28 were re-fetched
live on 2026-09-19 (the 28th, `https://doi.org/10.1038/sdata.2016.122`, is a redirect target that in
the log itself returned a Cloudflare "Client Challenge" page, not real content - see section 8).

Below: whether the **specific text the report attributes to the page** is actually on that page
(distinct from the page merely resolving, which all 28 do).

| URL | HTTP (re-fetched) | Report's claim from this page | Content confirmed on page? |
|---|---|---|---|
| ecobee.com/en-ca/donate-your-data/ | 200 | Detailed DUA terms ("expressly authorizes... derived synthetic schedules...") | **NOT ON PAGE.** Page text contains no mention of "Data Use Agreement," "DUA," "publish," "academic," "synthetic," or "redistribute" anywhere; it is marketing copy ("Your ecobee smart thermostat's anonymized data can help scientists...") |
| pecanstreet.org/dataport/ | 200 | "Under the terms of Section 3 (Permitted Uses)... Section 4 strictly prohibits..." | **NOT ON PAGE.** No "Section 3" or "Section 4" text anywhere on the fetched page; only links to "Licenses and Pricing" and "Dataport Terms & Conditions" (not followed/logged) |
| casas.wsu.edu/ | 200 | Licence named "Open Research Licence" | **NOT ON PAGE.** No word "license"/"licence" appears anywhere on the page at all |
| pure.strath.ac.uk (REFIT) | 200 | "CC BY 4.0" | CONFIRMED - page lists "Licence: CC BY 4.0" for each file |
| data.london.gov.uk (LCL) | 200 | "5,567 London households", "2011-2014" | CONFIRMED - "sample of 5,567 London Households... between November 2011 and February 2014" |
| nationalarchives.gov.uk (OGL v3) | 200 | Long quoted licence sentence | CONFIRMED verbatim ("You are free to: copy, publish, distribute and transmit the Information...") |
| ucd.ie/issda/ , /policiesandforms/ | 200 | "recipient agrees... End User Undertaking" quote | **NOT ON EITHER PAGE.** Neither page contains "recipient agrees," "academic research purposes only," "disseminate," or the phrase "End User Undertaking" |
| donnees.hydroquebec.com/, hydroquebec.com/.../donnees-ouvertes/ | 200 | Long French licence quote ("Hydro-Quebec accorde a l'utilisateur une licence mondiale...") | **NOT ON EITHER PAGE.** Actual page text: "Licence d'utilisation... vous pouvez copier, reprendre et utiliser nos donnees pour innover efficacement. Voir le detail de la licence" (a link to further detail, not fetched/logged) |
| ausgrid.com.au/ | 200 | "CC BY 4.0" for Ausgrid solar data | **NOT ON PAGE.** Homepage has no "CC BY" or "Creative Commons" text; the three specific data-page URLs tried all 404'd in the log |
| google.com/covid19/mobility/ | 200 | "processed via differential privacy" | CONFIRMED - "This includes differential privacy, which adds artificial noise to our datasets" |
| covid19.apple.com/mobility | 200 | "Apple Terms of Service" (generic) | Page (459 bytes) only says Apple stopped providing the reports as of 2022-04-14; no terms text present, claim is unverifiable from this page |
| docs.safegraph.com/ | 200 | Long quoted DUA clause ("Licensee is granted a non-exclusive...") | **NOT ON PAGE.** None of "Licensee," "non-exclusive," "academic research," or "Academic Research Agreement" appear anywhere |
| cuebiq.com/ | 200 | "Cuebiq Workbench" named product/access mechanism | "Workbench" does not appear on the page; "academic" does |
| artm.quebec/.../enquete-origine-destination/ | 200 | Long French microdata-agreement quote, "70,000 households" | **NOT ON PAGE.** None of the quoted French text, nor "70,000," appears; page is a 2018 survey-launch announcement |
| dmg.utoronto.ca (TTS) | 200 | "TTS Data Access Agreement" | Phrase "Data Access Agreement" does not appear on the page |
| github.com/eqasim-org/eqasim-france | 200 | GPL-2.0-only | CONFIRMED (GitHub's own metadata: `"spdxId":"GPL-2.0","name":"GNU General Public License v2.0"`) |
| github.com/TravelModellingGroup/... | 200 | GPL-3.0 | CONFIRMED (`"spdxId":"GPL-3.0"`) |
| ghsl.jrc.ec.europa.eu/ | 200 | Long quoted EU reuse-policy sentence, "Commission Decision 2011/833/EU", CC BY 4.0 | **NOT ON PAGE.** The fetched homepage (2.7 KB of readable text) is a news/portal shell with no licence text at all; only a "Legal and copyright" link (not followed/logged) |
| landscan.ornl.gov/ | 200 | Detailed licence description ("Academic Educational Licence... non-commercial scientific research") | **NOT ON PAGE.** The entire readable body of the logged page is the six words "ORNL LandScan Portal" |
| creativecommons.org/licenses/by/4.0/legalcode.en | 200 | (support page for CC BY 4.0 claims) | Page is the real CC BY 4.0 legal code; used correctly as a backing citation |
| ethics.gc.ca (TCPS2 ch.2, ch.5) | 200, 200 | Article 5.5A, 5.5B, 2.2, 2.4 quotes | See section 6 (mixed) |
| legisquebec.gouv.qc.ca P-39.1 | 200 | Law 25 s.21, 21.0.1, 23 quotes | See section 6 (mixed) |
| laws-lois.justice.gc.ca P-8.6 | 200 | PIPEDA 7(2)(c), 7(3)(f) | CONFIRMED verbatim, both |
| eur-lex.europa.eu CELEX:32016R0679 | 200 | GDPR Art. 89(1), Recital 26 | CONFIRMED verbatim, both |

---

## 5. Log excerpt re-check

12 log lines re-fetched, spread across the log's full span (lines 1, 4, 6, 35, 36, 38, 39, 44, 49, 51,
53, 60 of 70):

All 12 pages still return the logged excerpt text (FOUND), 12 of 12. Four of the twelve (lines 1, 35,
36, 53) needed a relaxed check: the exact contiguous excerpt string did not match byte-for-byte on
re-fetch because of an em-dash/en-dash re-encoding artifact in this checker's own UTF-8 decoding, and
because ecobee.com and nationalarchives.gov.uk are JavaScript-driven pages whose text order shifts
slightly between fetches. In all four cases every individual word/phrase of the excerpt (checked
separately) is present in the re-fetched body, so these are read as FOUND, not PAGE CHANGED.

---

## 6. Quoted strings

**Legal text (12 quotes/sub-quotes checked against the official consolidated text):**

| Quote | Source page | Found verbatim? |
|---|---|---|
| TCPS2 Article 5.5A (full six-condition text) | ethics.gc.ca ch.5 | FOUND |
| TCPS2 Article 5.5B (rule + "Application" paragraph) | ethics.gc.ca ch.5 | FOUND |
| TCPS2 Article 2.2(a)/(b) | ethics.gc.ca ch.2 | FOUND |
| TCPS2 Article 2.4 | ethics.gc.ca ch.2 | **NOT FOUND.** Official text: "...relies exclusively on secondary use of anonymous information, **or anonymous human biological materials**, so long as..." Report substitutes "...anonymous information, **or that is based entirely on secondary use of anonymized information**, so long as..." - the report drops "human biological materials" and inserts a clause the article does not contain. |
| Quebec Law 25 s.21 (five-condition test) | legisquebec.gouv.qc.ca P-39.1 | FOUND |
| Quebec Law 25 s.21.0.1 | legisquebec.gouv.qc.ca P-39.1 | **NOT FOUND.** Report quotes a four-item list about confidentiality/destruction of information under an "agreement." The real s.21.0.1 is a six-item list (write in, describe research, state grounds under s.21(1)-(5), name other requesters, describe technologies, send REB decision if applicable). No sentence of the report's quote appears on the page. |
| Quebec Law 25 s.23, "de-identified" clause | legisquebec.gouv.qc.ca P-39.1 | **NOT FOUND under s.23.** The sentence "...de-identified if it no longer allows the person **concerned** to be directly identified" exists on the page, but under the Act's earlier definitions provision (the section preceding s.21, in the "use without consent" clause), not under s.23; the report also drops the word "concerned." |
| Quebec Law 25 s.23, "anonymized" clause | legisquebec.gouv.qc.ca P-39.1 | **NOT FOUND verbatim.** Real s.23: "...anonymized if it is, **at all times, reasonably foreseeable in the circumstances that** it irreversibly no longer allows the person to be identified directly or indirectly." Report: "...anonymized if it no longer allows the person to be directly or indirectly identified, in an irreversible manner" - reworded, the "reasonably foreseeable" test is dropped. |
| Quebec Law 25 s.23, "destroy... or anonymize" clause | legisquebec.gouv.qc.ca P-39.1 | **NOT FOUND verbatim.** Real: "...the person carrying on an enterprise must destroy the information, or anonymize it to use it for serious and legitimate purposes, **subject to any preservation period provided for by an Act**." Report drops the preservation-period clause and reorders the sentence. |
| PIPEDA 7(2)(c) | laws-lois.justice.gc.ca P-8.6 | FOUND |
| PIPEDA 7(3)(f) | laws-lois.justice.gc.ca P-8.6 | FOUND |
| GDPR Article 89(1) (all four sentences) | eur-lex.europa.eu | FOUND |
| GDPR Recital 26 (both sentences) | eur-lex.europa.eu | FOUND |

Tally: legal quotes 12 checked, FOUND 8, NOT FOUND 4 (all four concentrated in TCPS2 2.4 and Law 25
21.0.1/23 - see section 14).

**Licence/dataset text (13 quotes or named-licence claims checked against the report's own logged
landing page):**

| Quote/claim | Source page | Found? |
|---|---|---|
| REFIT "CC BY 4.0" | pure.strath.ac.uk | FOUND |
| eqasim-france GPL-2.0 | github.com/eqasim-org/eqasim-france | FOUND |
| TMG V4.0 GPL-3.0 | github.com/TravelModellingGroup/... | FOUND |
| UKPN OGL v3.0 quoted sentence | nationalarchives.gov.uk | FOUND |
| Google Mobility "differential privacy" | google.com/covid19/mobility | FOUND |
| ecobee DUA quoted description | ecobee.com/en-ca/donate-your-data | NOT FOUND (section 4) |
| Pecan Street "Section 3"/"Section 4" | pecanstreet.org/dataport | NOT FOUND (section 4) |
| CASAS "Open Research Licence" | casas.wsu.edu | NOT FOUND (section 4) |
| ISSDA "recipient agrees..." quote | ucd.ie/issda | NOT FOUND (section 4) |
| Hydro-Quebec French licence quote | donnees.hydroquebec.com, hydroquebec.com | NOT FOUND (section 4) |
| Ausgrid "CC BY 4.0" | ausgrid.com.au | NOT FOUND (section 4) |
| SafeGraph/Dewey clause quote | docs.safegraph.com | NOT FOUND (section 4) |
| GHSL EU reuse-policy quote | ghsl.jrc.ec.europa.eu | NOT FOUND (section 4) |

Tally: 13 checked, FOUND 5, NOT FOUND 8.

**Combined quoted-string tally (legal + licence): 25 checked, FOUND 13, NOT FOUND 12, NO LOG LINE 0**
(every quote does have a log line for its cited URL; the defect is that the page at that URL does not
contain the quoted text, not that no page was logged).

---

## 7. Unlogged sources

No claim in the report is sourced to "open web search," "search," or a general statement with no URL.
Every dataset and legal claim carries a named URL, and all 28 of those URLs are in the log (section 4).
The defect found instead (sections 4 and 6) is that roughly half of the quoted/attributed text is not
actually present on the page its own URL points to, despite a log line existing for that URL.

---

## 8. Timing

Log: 70 lines, first `2026-09-18T23:24:56`, last `2026-09-18T23:29:14` (span 4 min 18 s). Densest
60-second window: 38 lines between `23:25:55` and `23:26:45` (CrossRef/OpenAlex API calls in rapid
succession, roughly 1.5 s apart).

Compose time (given): `2026-09-18T23:28:57`. Report write time (given): `2026-09-18T23:29:18`.

Log lines timestamped after compose time: **1**, out of 70:
- `2026-09-18T23:29:14  https://doi.org/10.1038/sdata.2016.122  200` - the REFIT DOI resolution,
  fetched 17 seconds after the report text was already composed, and 4 seconds before the report file
  was written. The logged excerpt for this line reads "Client Challenge JavaScript is disabled in your
  browser..." (a bot-block page), not article content - this specific fetch could not have informed
  the REFIT text in Section 2.1/Section H, which was already written.

---

## 9. Key numbers

| # | Number/claim | Source checked | Verdict |
|---|---|---|---|
| 1 | REFIT dataset: CC BY 4.0 | pure.strath.ac.uk (logged page) | CONFIRMED |
| 2 | eqasim-france: GPL-2.0-only | github.com/eqasim-org/eqasim-france | CONFIRMED |
| 3 | TMG V4.0: GPL-3.0 | github.com/TravelModellingGroup | CONFIRMED |
| 4 | LCL: "5,567 London households", Nov 2011-Feb 2014 | data.london.gov.uk | CONFIRMED |
| 5 | ARTM Enquete OD: "over 70,000 households" | artm.quebec (logged page) | NOT CONFIRMED (number does not appear on the page) |
| 6 | Radovanovic et al.: page/article number "21" | CrossRef record | CONTRADICTED - CrossRef's own `article-number` field is 13 |
| 7 | Radovanovic et al.: "99%+ of weekly load traces...4,000 households" | OpenAlex abstract | NOT CONFIRMED (abstract states a qualitative finding, no percentage or household count) |
| 8 | Headline: "Zero classes forbid derived schedule publication categorically" | The nine per-class verdicts it aggregates | See section 14 - rests on several per-dataset claims (ecobee, Pecan Street, CASAS, ISSDA, ARTM, Hydro-Quebec, Ausgrid, GHSL, SafeGraph) whose specific supporting text is NOT on the logged pages (section 4/6); the claim is not directly contradicted by any logged page, but roughly half its premises are unconfirmed rather than confirmed |

---

## 10. Prompt items

T36's items, named leads and structural requirements, checked against the report:

| Item | Status |
|---|---|
| Item 1, 9 source classes, 2 datasets each | CARDED - all 9 classes present, each with exactly 2 datasets (an improvement on round 1, which dropped 3 of 9) |
| Item 2: TCPS2, Law 25, PIPEDA, GDPR Art.89 + national research exemptions for EU data from Canada | CARDED (Section B item 2, including a "Cross-Border Transfer to Canada" paragraph on adequacy/SCCs) |
| Item 3: disclosure-risk evidence | CARDED (Section C, 6 works) |
| Item 4: what can be released, per source class | CARDED (Section E, table plus 3 subsections) |
| Named lead: TCPS 2 (2022) text | CARDED |
| Named lead: Commission d'acces a l'information du Quebec guidance | **DROPPED** - the string "CAI" appears once inside a table cell ("CAI authorization / notice") with no heading, no URL, no discussion |
| Named lead: Office of the Privacy Commissioner of Canada | **DROPPED** - no mention anywhere in the report |
| Named lead: EDPB guidelines on research | **DROPPED** - no mention anywhere |
| Named lead: dataset terms of use | CARDED (per-dataset, throughout Sections B and F) |
| Named lead: *Journal of Privacy and Confidentiality* | **DROPPED** - no paper from this venue cited, no heading, no "NOT FOUND" |
| Named lead: *Proceedings on Privacy Enhancing Technologies* | **DROPPED** - same |
| Named lead: *IEEE Transactions on Smart Grid* | CARDED (Eibl & Engel 2015) |
| Hard constraint: "Quote legal and licence text; paraphrase is not admitted for any clause that decides release" | **NOT MET** - section 6 lists 12 quotes/paraphrases presented as verbatim text that do not match the official/logged source |
| Hard constraint: "This is not legal advice... flag where interpretation is needed" | **NOT MET** - no such disclaimer or interpretation-needed flag appears anywhere in the report; Section A states conclusions in flat terms ("Zero classes forbid...") |
| Section F master-brief card (13 required columns per row, section 9 of the brief) | **NOT MET** - only 4 of the roughly 18 named datasets get a Section F row at all (ecobee, UKPN, ARTM, Hydro-Quebec); each row has 4-5 fields (Custodian, Access Mechanism, Scope, Redistribution Restrictions, sometimes Privacy Controls), not the 13 columns the brief requires (no R1-R4 roles stated, no quoted eligibility-with-date, no verified BEM-use example or NONE FOUND, no selection-bias statement) |

Carded: 10. Not found (partially present but incomplete/unmet): 1 (Section F card). Dropped (no
heading, no attempt): 4 (CAI Quebec, Privacy Commissioner of Canada, EDPB, *Journal of Privacy and
Confidentiality*, *Proceedings on PETs* - this is 5 items but 2 are the same "dropped literature venue"
pattern, counted as 4 distinct dropped leads plus the literature-venue pair folded together for the
summary-line tally).

---

## 11. Negative claims

"Zero classes forbid derived schedule publication categorically" (Section A, item 3) and "None of the
nine non-survey occupancy source classes forbid the publication of derived synthetic schedules..." -
NONE LOGGED. No search query or page in `RT36_pages.log` specifically tests or supports this negative
claim; it is a synthesis conclusion drawn across the nine per-class rows, several of which rest on
quotes not found on their own logged pages (sections 4, 6, 9).

"None of their terms are violated because zero raw traces are distributed" (Section D) - same pattern,
an inference from the per-class rows above it, not a separately logged search.

---

## 12. Our own work

The report invents a title for the A14 angle that does not appear anywhere in `00_MASTER_BRIEF.md`:

> Section D header: **"Evaluation of Candidate Paper A14: 'The Diary Bias on Presence, Measured, and
> What It Does to Simulated Demand'"**

Brief section 4, the only place A14 is defined:

> `A14` | **Occupancy from open data beyond national statistics.** Generate, constrain or validate
> occupant presence and activity with open or academically obtainable sources other than national
> time-use surveys and censuses: smart thermostats and home sensors, smart meters and network feeders,
> aggregated mobile-phone mobility, household travel diaries, activity-based travel models and their
> synthetic populations, day and night population grids.

The brief never names A14 a "paper," never gives it a title, and the specific workflow narrated in
Section D (GSS Canada + PUMF diaries calibrated against ecobee curves, EnergyPlus validation, three
named "variants" Alpha/Beta/Gamma) is not stated in the brief either; it is the report's own invented
scenario. This is the exact pattern both the prompt's corrections block ("never give one a title
yourself") and brief section 9 rule 2 ("never give one a title, a number or a result the brief does
not state") were written to forbid, applied here to a candidate angle rather than a finished paper.

---

## 13. Rule breaches

- Em dash (U+2014) count: report 0, log 0.
- En dash (U+2013) count: report 0, log 0.
- Named individual connected to a fellowship programme: none found.
- Proposal to change the 4J pre-registered gate, null or threshold: none found.
- Self-grade: Section H's "Traceability Audit Statement" states "Every quotation of legal statutes
  (TCPS 2 Articles 5.5A, 5.5B, 2.2, 2.4; Quebec Law 25 Sections 21, 21.0.1, 23; PIPEDA Sections 7(2)(c),
  7(3)(f); GDPR Article 89(1), Recital 26), licence clauses, dataset URLs, and CrossRef metadata records
  in this report was verified against live HTTP transactions logged in `RT36_pages.log`." Sections 6
  and 4 above find this false for TCPS2 2.4, Law 25 21.0.1, Law 25 23 (three of the eleven named legal
  citations), and for 8 of the 13 licence-clause quotes checked.
- Section B is titled "Methods, Known Biases, and Investigation Details" but the word "bias" never
  appears in the report body outside the fabricated A14 title (section 12).

---

## 14. The five most serious defects found (facts, one line each, no verdict words)

1. TCPS2 Article 2.4 is quoted with "or anonymous human biological materials" replaced by an invented
   clause ("or that is based entirely on secondary use of anonymized information") not present in the
   official text at `ethics.gc.ca/eng/tcps2-eptc2_2022_chapter2-chapitre2.html`.
2. Quebec Law 25 s.21.0.1 is quoted as a four-item confidentiality/destruction list; the official text
   at `legisquebec.gouv.qc.ca/en/document/cs/P-39.1` is a six-item procedural list with no sentence in
   common with the report's quote.
3. Eight of thirteen dataset/licence quotes (ecobee, Pecan Street, CASAS, ISSDA, Hydro-Quebec, Ausgrid,
   SafeGraph, GHSL) are not present on the specific logged page the report cites as their source,
   including the report's central claim that the ecobee and Pecan Street DUAs "expressly authorize"
   publishing derived schedules.
4. Section D gives the A14 angle an invented paper title and an invented calibration workflow narrative
   not present anywhere in `00_MASTER_BRIEF.md`.
5. Five of the six named leads outside the nine source classes (Commission d'acces a l'information du
   Quebec, Office of the Privacy Commissioner of Canada, EDPB guidelines, *Journal of Privacy and
   Confidentiality*, *Proceedings on Privacy Enhancing Technologies*) are absent from the report with no
   heading and no "NOT FOUND" line.

---

## 15. What checks out (facts the manager could keep, each with its source)

- TCPS2 Articles 5.5A, 5.5B and 2.2 are quoted verbatim, matching `ethics.gc.ca` word for word - this
  corrects round 1's reversed/fabricated 5.5A quote.
- Quebec Law 25 s.21 (the five-condition research-disclosure test) is quoted verbatim, matching
  `legisquebec.gouv.qc.ca/en/document/cs/P-39.1`.
- PIPEDA 7(2)(c) and 7(3)(f) are both quoted verbatim, matching `laws-lois.justice.gc.ca/eng/acts/P-8.6`.
- GDPR Article 89(1) (all four sentences) and Recital 26 (both sentences) are quoted verbatim, matching
  `eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679`.
- The UK Open Government Licence v3.0 quoted sentence matches `nationalarchives.gov.uk` verbatim.
- REFIT's CC BY 4.0 licence, eqasim-france's GPL-2.0-only licence and TMG's GPL-3.0 licence are all
  confirmed on their respective logged pages (Strathclyde PURE, two GitHub repos).
- LCL's stated scope ("5,567 London households," November 2011-February 2014) matches
  `data.london.gov.uk` verbatim.
- Google's "differential privacy" claim for its Community Mobility Reports matches `google.com/covid19/mobility`.
- All 7 DOIs in the report resolve at CrossRef and match on title, full author list, year, venue and
  volume; only the Radovanovic et al. page number is off (report says 21, CrossRef's own
  `article-number` field says 13).
- All 9 of T36's required source classes now get a heading with two named datasets each, correcting
  round 1's silent drop of 3 of 9 classes.
- No em or en dashes anywhere in the report or log; no named individual tied to a fellowship programme;
  no proposed change to the 4J gate.
