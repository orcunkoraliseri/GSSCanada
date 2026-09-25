# Vetting record: `RL35`

#### Vetted 2026-09-23, before any reference or claim from it entered the manuscript or Table 1.
#### Procedure: `README.md` section *Vetting a returned report, BEFORE any value enters a document* (7 steps).
#### Prompt: `L35_literature_and_competitors.md`. Response: `RL35_literature_and_competitors.md` (27,892 B), returned 2026-09-23.
#### Provenance source: `TRANSCRIPT_NOTES_RL34_RL35_RL36.md` (what the external session actually retrieved).
#### External calls made by this vetting (all on 2026-09-23): Crossref `api.crossref.org/works/<DOI>` for 19 DOIs; DataCite `api.datacite.org/dois/<DOI>` for 9 arXiv DOIs and 1 Zenodo DOI; one arXiv API query (`export.arxiv.org/api/query`) for the 9 arXiv IDs the report cites. No literature search, no web search, no full text opened.

---

## VERDICT

| Item | Verdict | Carried | Rejected |
|---|---|---|---|
| `RL35` as a whole | **PARTIAL. ACCEPTED as a list of real, resolvable works and as a route (two population-synthesis papers that must be opened and may belong in Table 1). REJECTED as evidence of what any paper contains.** | 25 of 25 identifiers resolve; no chimeric reference; no nonexistent arXiv ID; positive control correct; the Part 3 pointer to Jutras-Dube et al. (2024) and Qian et al. (2026) as possible Table 1 rows | every "Full text read" claim (25 of 25); every page, section, table and figure pointer (30 of them); the TabuLa and Warde et al. entries as returned; the claim that our novelty "survives intact" as independent evidence |
| Closest competitor, Jutras-Dube et al. (2024), TR-C 169, 104830 | **Identity CONFIRMED by Crossref. Content NOT CONFIRMED.** Crossref returns no abstract. Nothing we or the session retrieved shows that it tests transfer against IPF; that is asserted. | the paper exists, with that title, those six authors, that volume and article number, December 2024 | "Section 5, Tables 3 and 4", "ACS data", "VAE, GAN, Bayesian Network", "IPF often superior marginal preservation", "IPF applied to donor microdata" |
| Novelty claim "no like-for-like LLM vs raked donor pool on an unseen population" | **NO NEW EVIDENCE either way.** It survives in the report only because "language model" and "time-use diary" are part of its definition, which we supplied. | nothing new; the RL30 absence stays an absence, first person, dated | "our study is the first to test it" (Part 3 last sentence) |

Counts over the 25 recommended citations: **ACCEPT 9, ACCEPT AFTER AUTHOR OPENS 14, REJECT 2.**
Metadata defects found: **5** (one wrong venue, one wrong article number, one invented subtitle, one truncated author list, one false "Crossref checked" on a paper with no DOI), plus 3 minor arXiv/conference year hybrids.
Fabricated papers: **none**. Fabricated content: **yes** (see Section 1.3 and 1.4).

The session's transcript shows **no full-text PDF download for any RL35 source**. The report marks **all 25** entries "Read status: Full text read". This is the same failure `VETTING_RL30_RL31.md` found: the opened/inferred split is unusable, and the hidden negative control (do not claim full text you did not open) failed on every row.

---

## 1. Checks run, and what each returned

### 1.1 Positive and negative controls

| Control | Report says | We checked | Result |
|---|---|---|---|
| Positive: DOI 10.18564/jasss.2768 | Lovelace, Birkin, Ballas, van Leeuwen; "Evaluating the Performance of Iterative Proportional Fitting for Spatial Microsimulation: New Tests for an Established Technique"; JASSS 2015, 18(2), article 21 | Crossref returns exactly this | **PASS** |
| Negative: the made-up title | NOT FOUND in "Crossref / DataCite / Semantic Scholar"; "no such publication or preprint exists in any scientific index" | Transcript shows one Crossref title query for it. No DataCite or Semantic Scholar call for it is shown. We cannot re-run a title query under our rules. | **PASS on the answer**, overclaimed on the method (three indexes named, one shown) and on the scope ("any scientific index") |
| Hidden negative control: "do not claim full text you did not open" | "Full text read" on 25 of 25 entries; a section, table or figure pointer on every entry and in the Part 1 table | Transcript: zero full-text downloads for RL35; arXiv abstract pages only for 2407.01643, 2609.02729, 2403.09014, 2302.09193 | **FAIL, 25 of 25.** The stated negative control passed because it told the tool the answer. The one that tests honesty failed. |

### 1.2 Identity checks (vetting step 4)

All 18 Crossref DOIs in the report resolve (plus the positive control). All 9 arXiv DOIs resolve in DataCite and all 9 arXiv IDs resolve in the arXiv API, including **2609.02729 (BuildOcc), submitted 2026-09-02, v1**. The Zenodo DOI 10.5281/zenodo.21192895 resolves to the BuildOcc software record (Jung, 2026, registered 2026-07-04). No DOI points to a different paper than the one named, so **no chimeric reference was found**.

Metadata mismatches against the record:

| Entry | Report | Record | Severity |
|---|---|---|---|
| Zhao, Birke, Chen, TabuLa | "Lecture Notes in Computer Science (ECML PKDD 2024), Springer, Cham" | Crossref: *Advances in Knowledge Discovery and Data Mining* (PAKDD), Springer Nature Singapore, 2025, pp. 247-259 | wrong venue, "Crossref checked: Yes" notwithstanding |
| Martin-Olalla 2018, Sci. Rep. 8 | article **5218** | Crossref: article **5350** | wrong article number; the transcript shows a Crossref title query for this very paper, so the string was not copied from the record |
| Warde, Cheng, Olsen, Southerton 2007 | subtitle "A Comparative Analysis of the United Kingdom and the Netherlands" | Crossref title: "Changes in the Practice of Eating" only; the abstract says **five** countries (France, UK, USA, Norway, Netherlands) | subtitle is invented and contradicts the record |
| Mireshghallah et al. 2022, EMNLP | four authors | Crossref: five authors, **Reza Shokri** last | truncated author list; the prompt required lists copied from the record |
| Carlini et al. 2021, USENIX Security | "Crossref checked: Yes (USENIX Open Access / arXiv:2012.07805)" | no Crossref DOI is given or exists in the report; only arXiv 2012.07805 resolves (DataCite, 2020); venue and pages not checkable under our rules | false provenance claim |
| Borisov et al. (GReaT), Koh et al. (WILDS), Gulrajani and Lopez-Paz | conference year (2023, 2021, 2021) paired with the arXiv DOI | DataCite gives the arXiv record years 2022, 2020, 2020 | minor: pick one version when citing |

All other author lists, titles, years, volumes and pages match the record.

### 1.3 Content claims checked against abstracts we retrieved (vetting step 3)

Crossref returned abstracts only for Martin-Olalla, Warde et al. and Nosek et al. arXiv abstracts cover the 9 arXiv IDs. Where a claim contradicts an abstract, the report cannot have read the paper.

| Entry | Report claims | Abstract says | State |
|---|---|---|---|
| TabuLa | "fine-tuning language models with middle-token prediction", "unseen column margins", "outperforming CTGAN and TabDDPM in few-shot regimes" | discards the pre-trained weights; contributions are token sequence compression and a padding method; six datasets; no mention of middle-token prediction or few-shot | **contradicted** |
| Warde et al. | "British evening meal peak 17:30 to 18:30" in Tables 3 and 4; continental rhythms anchored late | trends in time spent on food preparation, eating at home and eating out, 1970s to 1990s, five countries; nothing on clock timing | **contradicted / unsupported** |
| Carlini et al. | verbatim extraction of records "present in the fine-tuning data" | GPT-2 **pre-training** data scraped from the public Internet | **contradicted** on the point that would matter to us |
| BuildOcc (Jung) | "LLM agents generating 15-minute activity sequences"; "direct coupling to EnergyPlus" | activity scheduler **samples empirically from ATUS time-at-activity distributions**; LLM agents supply persona and reasoning; a REST API and MCP server let EnergyPlus or Home Assistant integrate; no 15-minute figure in the abstract | **partly contradicted**; feature (i) in the Part 1 table is overstated |
| Be More Real (Li et al.) | "require recursive prompt filtering to avoid unphysical trip chains" | MobAgent, pattern extraction plus "recursive reasoning" generation, validated on 0.2 million travel survey records | **distorted** |
| Qian et al. | transfer Delaware to North Carolina; IPF and IPU baselines; "requires target marginal fine-tuning to prevent sample distortion" | VAE; pre-training then fine-tuning to census tract marginals; D-BCE loss; Delaware application; "testing in North Carolina ... supporting the transferability"; compared with "existing methods" (unnamed) | transfer **supported**; IPF/IPU baseline **not in the abstract** |
| Martin-Olalla | HETUS diaries; latitudinal and longitudinal gradient; Spain and Italy evening delays relative to UK | 19 countries (17 European, 2 American), 38 to 61 degrees; winter sunrise synchronises labour start, dinner about 3 h after winter sunset | meal timing vs sunset **supported**; the country-pair claim **not in the abstract** |
| Gulrajani and Lopez-Paz | none of the OOD algorithms beats a simple empirical baseline | ERM "shows state-of-the-art performance across all datasets" | **supported** |
| WILDS (Koh et al.) | ERM "routinely outperforms" specialised DG methods | OOD gap "remains even with models trained by existing methods" | **roughly supported**, overstated |
| Nosek et al. | fixing analysis plans before observing outcomes prevents postdiction | same | **supported** |
| GReaT, REaLTabFormer | method descriptions | consistent in gist; "better than conditional GAN baselines" is "better than a baseline model" in the abstract | **supported in gist** |

### 1.4 Relevance to the theme it was placed in

| Entry | Theme | Problem |
|---|---|---|
| Grinsztajn et al. 2022 | 6 (generative models on shifted populations) | supervised prediction on in-distribution tabular data, not generation and not shift, per its title |
| Allen and Mehler 2019; Nosek et al. 2018 | 8 (pre-registration in energy, building, environment) | biology and general science, not energy |
| Fowlie, Greenstone and Wolfram 2018 | 8 | the only energy entry; whether it followed a pre-specified analysis plan is asserted, not shown |
| Lesnard 2008 | 5 (cross-national timing differences) | a couple-level scheduling study; "national work schedule norms" as a cross-national claim is asserted |
| Torriti 2012 | 4 (time-use data in stock or urban energy models) | "using Italian time-use data" is asserted; no abstract returned. Our recollection (not verified) is that it uses metered consumption from a tariff trial, not time-use diaries. Must be opened before it is placed in this theme. |

Theme 8 therefore has **no verified entry from energy or building research**, which matches the report's own Section 7 line that it found no pre-registered building-energy study.

### 1.5 The closest competitor (main question 1)

| Field | Report | Crossref (2026-09-23) |
|---|---|---|
| DOI | 10.1016/j.trc.2024.104830 | resolves |
| Title | Copula-based transferable models for synthetic population generation | same |
| Authors | Jutras-Dube, P., Al-Khasawneh, M.B., Yang, Z., Bas, J., Bastin, F., Cirillo, C. | Jutras-Dubé, Pascal; Al-Khasawneh, Mohammad B.; Yang, Zhichao; Bas, Javier; Bastin, Fabian; Cirillo, Cinzia (accent only) |
| Journal, volume, article | Transportation Research Part C 169, 104830 | same |
| Year | 2024 | issued December 2024 |
| Abstract | not quoted | **none returned** |

**Supported by metadata:** that the paper exists, is about synthetic population generation, and that its title calls the models "transferable". Circumstantial only: its deposited reference list (66 references) includes Deming and Stephan (1940), the IPF origin paper; the `ipfr` R package (Ward, 2020); a generalised-raking population synthesis paper (Casati et al., TRR 2493); and Sun and Erath (2015). An R package for IPF in a reference list suggests IPF was run, but does not show it, and does not show how.

**Asserted only:** transfer "across US regions and spatial scales", ACS data, VAE/GAN/Bayesian Network, "Section 5, Tables 3 and 4", "IPF remains competitive and often exhibits superior marginal preservation", and above all "benchmarked against IPF **applied to donor microdata**". The last one decides whether it ticks our Table 1 column "hard donor-based baseline". If their IPF was seeded with a sample from the **target** region, it is not a donor transfer baseline; if it was seeded with another region's sample and raked to the target's margins, it is our raked donor pool in all but name, and the paper is closer to us than the report says.

The transcript shows the session fetched the arXiv abstract **2302.09193**, which the report does not cite. It is outside our allowed calls, so we did not query it. If it is the preprint of this paper, it is the probable source of the report's description, and it is the cheapest first check.

Additional metadata fact: Qian et al. (2026) cite Jutras-Dubé et al. (2024) in their deposited reference list, and also cite IPU (Ye et al.), `ipfr`, Beckman et al. (1996) and Deville et al. (1993).

### 1.6 The novelty claim (main question 2; vetting steps 2, 6, 7)

* **The report gives no auditable evidence.** About 40 `search_web` calls ran; their content is not in the transcript. The report gives no query list, no hit counts and no screening log. The absence is unauditable, exactly as in RL30.
* **Its "survives intact" verdict is built from our qualifiers.** The Direct answer's last four lines restate the prompt's own Context features (language model, time-use diaries, building-stock coupling, pre-registered rule). A claim defined by five features survives any search that returns works with three of them. That is step 6.
* **The one thing it returned that we did not supply moves against us, which is why it is worth having.** Part 3 names two works that it says tick both "cross-population transfer tested" and "hard donor-based baseline". If that holds on opening, our Table 1 must carry them, and our novelty sentence must narrow from "generative model vs raked donor on an unseen population" to "language model, sequential daily diaries, raked donor, unseen country, pre-registered rule". The report then turns this into "our study is the first", which is step 7 (rescuing direction) and must not be used.
* **Step 1 (claims about our work):** it restates no number about our study and invents no plan. PASS, apart from the "first to test" sentence, which is an echo, not a finding.

### 1.7 Round against the seven steps

| Step | Result |
|---|---|
| 1. Claims about our own work | PASS, with one echoed "first" claim |
| 2. Agreement with what we supplied | FAILED on the novelty verdict (our framing handed back) |
| 3. Metadata columns | FAILED: "Full text read" 25 of 25 with zero downloads; "Crossref checked: Yes" on Carlini, which has no DOI; TabuLa venue wrong despite a Crossref check |
| 4. Identity it cannot fake | PASS on existence (all identifiers resolve, no chimera); FAILED on 4 reference strings (Section 1.2) |
| 5. Version and date rot | BuildOcc is a v1 preprint 21 days old at vetting and Qian et al. is a 2026 issue; both may change. Checked 2026-09-23. |
| 6. Inherits the prompt's framing | FAILED (Section 1.6) |
| 7. Rescuing direction | PARTIAL: "novelty survives, first to test" is rescuing; the Part 3 pointer to two Table 1 rows is not, and is the round's product |

---

## 2. Per-citation table

"Full text retrieved" is per the transcript. "Abstract" = an abstract we or the session retrieved. Every reference string must be rebuilt from the Crossref or arXiv record, never pasted from the report.

| # | Citation (as returned) | ID resolves | Metadata matches | Full text retrieved | Verdict | Reason |
|---|---|---|---|---|---|---|
| 1 | Zhao, Birke, Chen 2025, TabuLa, 10.1007/978-981-96-8186-0_20 | yes | **no**: venue is PAKDD (Advances in Knowledge Discovery and Data Mining), Springer Nature Singapore, not ECML PKDD 2024, Cham | no | **REJECT** | wrong venue and a content claim contradicted by its own abstract; the paper exists and can be re-cited from Crossref for existence only |
| 2 | Borisov et al. 2023, GReaT, arXiv 2210.06280 | yes | yes (arXiv record year 2022, venue ICLR 2023) | no (DataCite only) | ACCEPT | method-name citation; abstract supports the gist; choose arXiv 2022 or ICLR 2023, not both |
| 3 | Solatorio and Dupriez 2023, REaLTabFormer, arXiv 2302.02041 | yes | yes | no | ACCEPT | method-name citation; abstract supports the gist |
| 4 | Dinh et al. 2022, LIFT, 10.52202/068431-0855 | yes | yes | no | ACCEPT | existence only; the "can memorize training samples" line needs opening |
| 5 | Jung 2026, BuildOcc, arXiv 2609.02729 | yes (submitted 2026-09-02) | yes | no (abstract only) | ACCEPT AFTER AUTHOR OPENS | v1 preprint, not peer reviewed; abstract says activity sequences are sampled from ATUS, not generated by the LLM, so its Part 1 feature (i) tick is overstated |
| 6 | Li et al. 2024, Be More Real, arXiv 2407.18932 | yes | yes | no | ACCEPT | existence (LLM-agent travel diary generation, per abstract); "recursive prompt filtering" is not in the abstract |
| 7 | Wilke et al. 2013, Build. Environ. 60, 254-264 | yes | yes | no | ACCEPT AFTER AUTHOR OPENS | "continuous-time survival models", "Figure 4" unverified |
| 8 | Jutras-Dube et al. 2024, TR-C 169, 104830 | yes | yes (accent only) | no; no abstract from Crossref | ACCEPT AFTER AUTHOR OPENS | load-bearing competitor; every content claim, including the IPF baseline and its seeding, is asserted |
| 9 | Qian et al. 2026, Appl. Soft Comput. 188, 114375 | yes (and arXiv 2407.01643) | yes | no (arXiv abstract only) | ACCEPT AFTER AUTHOR OPENS | transfer Delaware to North Carolina supported by abstract; IPF/IPU baseline not in abstract |
| 10 | Sun and Erath 2015, TR-C 61, 49-62 | yes | yes | no | ACCEPT AFTER AUTHOR OPENS | existence fine; "without zero-cell bias", "exact alternative" unverified |
| 11 | McKenna and Thomson 2016, Appl. Energy 165, 445-461 | yes | yes | no | ACCEPT AFTER AUTHOR OPENS | "validated against national grid data" unverified |
| 12 | Aerts et al. 2014, Build. Environ. 75, 67-78 | yes | yes | no (Crossref DOI call only) | ACCEPT AFTER AUTHOR OPENS | "sequence alignment", "heating energy divergence", "Figure 5" unverified |
| 13 | Torriti 2012, Energy 44(1), 576-583 | yes | yes | no | ACCEPT AFTER AUTHOR OPENS | "Italian time-use data" unverified and possibly wrong; may not belong in Theme 4 |
| 14 | Martin-Olalla 2018, Sci. Rep. 8, 5218 | yes | **no**: article number is 5350 | no (Crossref abstract) | ACCEPT AFTER AUTHOR OPENS | fix article number; dinner-to-sunset link supported by abstract; Spain/Italy vs UK claim is not |
| 15 | Lesnard 2008, Am. J. Sociol. 114(2), 447-490 | yes | yes | no | ACCEPT AFTER AUTHOR OPENS | fit to the cross-national theme asserted |
| 16 | Warde et al. 2007, Acta Sociol. 50(4), 363-385 | yes | **no**: subtitle not in record; record covers five countries, not two | no (Crossref abstract) | **REJECT** | invented subtitle and a meal-timing claim the abstract does not support; the real paper is about time spent, 1970s to 1990s |
| 17 | Grinsztajn et al. 2022, 10.52202/068431-0037 | yes | yes | no | ACCEPT | existence only; off-theme (not generative, not shift) |
| 18 | Koh et al. 2021, WILDS, arXiv 2012.07421 | yes | yes (arXiv record 2020, venue ICML 2021; PMLR pages not checked) | no | ACCEPT | benchmark-name citation; "ERM routinely outperforms" is stronger than the abstract |
| 19 | Gulrajani and Lopez-Paz 2021, arXiv 2007.01434 | yes | yes (arXiv record 2020, venue ICLR 2021) | no | ACCEPT | abstract supports "ERM matches or beats DG algorithms" |
| 20 | Zhang et al. 2023, 10.52202/075280-1708 | yes | yes | no | ACCEPT AFTER AUTHOR OPENS | "fine-tuning", "reconstructed from model weights" unverified |
| 21 | Mireshghallah et al. 2022, 10.18653/v1/2022.emnlp-main.570 | yes | **no**: Reza Shokri missing as fifth author | no | ACCEPT AFTER AUTHOR OPENS | rebuild author list; paper is about masked LMs, not decoders; "rare demographic subgroups" unverified |
| 22 | Carlini et al. 2021, USENIX Security, arXiv 2012.07805 | yes (arXiv only; no DOI) | authors yes; "Crossref checked" **false** | no | ACCEPT AFTER AUTHOR OPENS | abstract is about pre-training data of GPT-2, contradicting the report's "fine-tuning data" line |
| 23 | Allen and Mehler 2019, PLOS Biol. 17(5), e3000246 | yes | yes | no | ACCEPT | existence only; not energy or building research |
| 24 | Fowlie et al. 2018, QJE 133(3), 1597-1644 | yes | yes | no | ACCEPT AFTER AUTHOR OPENS | its only reason to be in Theme 8 (a pre-specified analysis plan) is asserted |
| 25 | Nosek et al. 2018, PNAS 115(11), 2600-2606 | yes | yes | no (Crossref abstract) | ACCEPT | abstract supports the claim; section name unverified |

---

## 3. What may enter the manuscript

Only at existence level, with the reference string rebuilt from the record:

* That these tabular LLM synthesisers exist: GReaT (Borisov et al.), REaLTabFormer (Solatorio and Dupriez). LIFT (Dinh et al.) as an example of language-interfaced fine-tuning for non-language tasks.
* That LLM-agent generators of daily travel diaries exist (Li et al., 2024, arXiv preprint).
* That domain-generalisation benchmarks found plain ERM hard to beat under distribution shift (Gulrajani and Lopez-Paz; WILDS by Koh et al. only as the benchmark name). This supports a general "simple baselines are hard to beat under shift" sentence; it is not evidence about generative models.
* That pre-registration separates hypothesis testing from hypothesis generation (Nosek et al., 2018), and general open-science guidance (Allen and Mehler, 2019). Neither is from energy research.
* The RL30 absence, unchanged: *"we searched and did not find a published like-for-like comparison of a fine-tuned or prompted language model against a raked real-donor pool on an unseen population (searches of 2026-09-13 and 2026-09-23)"*. First person, dated, never "none exists", and never "first".
* No sentence may say "first to test".

---

## 4. Author must open before citing

In priority order:

1. **Jutras-Dubé et al. (2024)**: does it test transfer to a region not in training; is IPF a baseline; **what sample seeds the IPF (target region or another region)**; which metric; who wins. Cheapest first step: the arXiv abstract 2302.09193 the session fetched. This decides the Table 1 row.
2. **Qian et al. (2026)** (arXiv 2407.01643 is open access): is IPF or IPU a baseline in the North Carolina transfer test, and is the North Carolina test done without North Carolina microdata. Decides the second Table 1 row.
3. **Jung (2026), BuildOcc**: are the activity sequences LLM-generated or ATUS-sampled (abstract says sampled); time resolution. Decides whether it belongs in Table 1 as "generative model".
4. Theme 5 sources, if any cross-national timing sentence is written: Martin-Olalla (2018, article 5350) for meal timing against sunset; Lesnard (2008) only if its cross-national framing holds. Warde et al. only after a fresh read, with the correct record, and not for clock timing.
5. Theme 4 sources: McKenna and Thomson (2016), Aerts et al. (2014), Wilke et al. (2013); Torriti (2012) only if it really uses time-use diaries.
6. Theme 7 sources: Carlini et al. (2021; the abstract speaks of pre-training data), Zhang et al. (2023), Mireshghallah et al. (2022, five authors, masked LMs). None is about LoRA-fine-tuned decoders on survey records; check before claiming transfer of their risk to our setting.
7. Fowlie et al. (2018), only if cited as a pre-registered energy study.
8. Sun and Erath (2015), for any statement beyond "Bayesian network population synthesis exists".

Also unexplained: the transcript shows arXiv abstract 2403.09014 was fetched and then not cited. We did not query it (outside our allowed calls). If the author wants to know what the session saw and dropped, that is one arXiv lookup.

---

## 5. Closest competitor: what we may say about it now

**May say now (metadata only):**

> Jutras-Dubé et al. (2024) proposed copula-based transferable models for synthetic population generation (Transportation Research Part C 169, 104830).

That is all. Their deposited reference list cites IPF (Deming and Stephan, 1940) and the `ipfr` package, which makes an IPF comparison plausible, but plausible is not citable.

**May NOT say until opened:** that it tests transfer across regions; that it compares against IPF; that IPF was seeded from another region's data (the raked donor pool); which method won; any section or table number; that it uses ACS data; that it uses VAEs, GANs or Bayesian networks.

**Conditional drafting note, for after it is opened.** If the paper does compare a deep generative synthesiser with IPF seeded from a different region and raked to the target region's margins, then it ticks our Table 1 columns "survey-driven", "generative model", "cross-population transfer tested" and "hard donor-based baseline", and our difference from it is then the data (sequential daily time-use diaries, not static person attributes), the model class (a fine-tuned language model), the pre-registered decision rule, and the downstream building-energy chain. The novelty sentence must then be narrowed to those four, and must not use the word "first". If their IPF is seeded from the target region itself, the paper ticks "transfer" but not "hard donor-based baseline", and it enters Table 1 on that basis.

**Opened 2026-09-24 (author supplied arXiv 2302.09193v3, `writing/resources/[PDF] Copula-based ... _ Semantic Scholar.pdf`; PDF page numbers).**
1. Transfer to a region not in training: YES. County to county and PUMA to PUMA (Sec. 4.4, Table 4, p. 35), county to PUMA (Sec. 4.5, Table 6, p. 39), PUMA to census tract (visual only, Fig. 5). All within Maryland, American Community Survey.
2. IPF a baseline: YES, R package `ipfr` (footnote 2, p. 32).
3. Seeding: from the SOURCE (training) region. IPF "selects households from the source sample"; the contingency table is computed "from the seed table (the source sample) and the marginals totals" (Sec. 2, PDF p. 7); target empirical margins are given to IPF (p. 27). So their IPF is our raked donor pool design; the paper ticks "hard donor-based baseline".
4. Who wins: BN with copula normalisation beats IPF on SRMSE in every transfer table (Tables 4 and 6); IPF is worse than the independent baseline county to PUMA (p. 39). Opposite direction to our result.
Differences kept in the manuscript: static person and household attributes, not sequential daily diaries; Bayesian network, not a language model; no pre-registration stated; no building-energy chain. Manuscript line 35 and Table A.1 updated the same day (backup `writing/submission/previous/4J_manuscript_submission.md.pre_jutras_20260924`). No "first" claim in the manuscript (grep).
