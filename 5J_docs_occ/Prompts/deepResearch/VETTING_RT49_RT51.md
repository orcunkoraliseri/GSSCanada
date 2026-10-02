# Vetting RT49, RT50, RT51 (European time-use diary access), 2026-10-01, 5J vetting employee

Reports: `RT49_hetus_country_data_access.md` + `RT49_pages.log` (25 lines), `RT50_open_timeuse_microdata_downloads.md` +
`RT50_pages.log` (26 lines), `RT51_timeuse_application_routes.md` + `RT51_pages.log` (21 lines), returned by the author's
outside tool. Prompts T49, T50, T51. Stray file `statbel_microdata.txt` (a bot-check page: "What code is in the image?").
Vetted offline only: no web access, no URL opened, no data file opened. Checks are against the files, our own records,
arithmetic and the three reports against each other.

Verdicts: **RT49 MIXED** (Eurostat, Progedo, German public-use file and MTUS rows rest on pages logged as read; most other
country rows rest on no logged page). **RT50 MIXED** (the narrow answer "only Spain, Italy and the German public-use file are
open" is cautious and plausible; the per-country detail around it is filler). **RT51 FAIL** for its quoted statements (eleven
eligibility quotes come from pages it logged as partial or never logged); salvage its route only (order lil-0695; Eurostat two
steps; German scientific-use file is EU/EEA only).

## Checks

### 1. Controls

| Report | Positive control | Negative control | Result |
|---|---|---|---|
| RT49 | Spain open INE, CC BY 4.0; Italy ISTAT public-use file | "HETUS-PUF-2010-v9" -> NOT FOUND | Pass, but the positive values were supplied in the prompt, so they show little |
| RT50 | Same Spain and Italy rows | Iceland "TUS2010_PUF.csv" -> NOT FOUND | Pass, same caveat |
| RT51 | France request 38663 (our record) | "HETUS-RA-2025 ... call 7" -> NOT FOUND | Negative pass; the France "control" only repeats what we told it (approved 2026-09-29, lil-1065 not granted) and adds an unsourced reason |

* The three negative controls all came back NOT FOUND. Good, but each negative search is overstated: RT50 says it searched
  "the Statistics Iceland portal and DataCite registry" while its log has one Iceland line marked partial and no DataCite line;
  RT51 says "an exhaustive search ... and historical call archives" with one logged Eurostat page.
* Positive-control details we did not supply (Spain 10-minute slots, members 10+, region, weights; Italy macroregion, all
  members; file names `datos_emptiem0910.zip`, sizes "34 MB compressed (~250 MB uncompressed)" and "~15 MB") are consistent
  with the files 5J already uses, but were not re-checked here against our held copies. The manager can compare the Spain
  file name and the two sizes with our own downloads in one step (not a UK file, allowed).
* Across reports the control results agree. That is weak evidence: these are three runs of the same tool, and RT49 even cites
  RT48 by name, so shared claims (see the UK sentence in check 6) are carried, not found again.
* RT51 does not answer the template's four standard questions (it substitutes its own four), so it never states which
  documents it opened in full.

### 2. Pages read versus claims

Log counts against the reports' own statements:
* RT49 log: 22 lines full, 3 partial (Insee, Statbel, CBS). Section G says 14 opened in full and 6 described, and lists
  Finland, Austria and Poland as "described" although no page for them is in the log. Norway, Greece, Romania, Serbia, Turkey
  and Hungary have rows in Section F and no logged page at all.
* RT50 log: 10 full, 16 partial. Its Section G list matches, except Denmark and Sweden ("described", not logged) and
  Switzerland (row in Section F, neither logged nor listed).
* RT51 log: 9 full, 12 partial. `https://commande.progedo.fr/` and `https://sikt.no/en`, both given as routes, are not in
  its log.
* RT49 and RT50 both answer "Did you invent ... any number?" with "No ... all ... verified directly against live servers".
  Their own logs (3 and 16 partial pages, plus unlogged countries) contradict this.

**Unsupported quotes and terms** (quoted eligibility sentences or licence terms from a page the log marks partial, a page not
in the log, or a page the report says it could not open). None of these may be cited or relied on:

| # | Report | Country | Claim | Why unsupported |
|---|---|---|---|---|
| U1 | RT49 F | Belgium | "The institution's statute, mission or stated purpose must include statistical or scientific research"; 0 EUR (500 EUR custom); 4 to 8 weeks; Belnet Filesender | Statbel page partial; RT49 G says "access restricted by Cloudflare challenge"; `statbel_microdata.txt` is the bot-check page, so the page text was never read |
| U2 | RT51 F | Belgium | "Statbel grants access to microdata for scientific research to researchers from Belgian and foreign universities."; "Public cloud LLM ingestion forbidden" | Same captcha page, logged partial. RT49 and RT51 "quote" two different sentences from a page neither could read |
| U3 | RT50 F | Belgium | "SPSS / Stata via application, ~30 MB" | Same page; a file size for a file nobody saw |
| U4 | RT49 F, E | Netherlands | "~2,100 EUR project fee plus monthly per-user fees"; 6 to 10 weeks; "no external tools, no cloud AI, no internet in enclave" | CBS page logged partial; RT49 G lists it as described only |
| U5 | RT51 F | Austria | "Access to microdata via the AMDC is open to accredited scientific research institutions worldwide pursuant to Section 38a of the Federal Statistics Act." | Source is the statistik.at home page, logged partial |
| U6 | RT51 F | Finland | "Microdata are provided for scientific research. User licences can be granted to foreign researchers following institutional verification."; fee "~150-300 EUR" | stat.fi page logged partial |
| U7 | RT51 F, E | Norway | "Data can be ordered by students and researchers at universities and research institutions in Norway and abroad for research purposes."; 1 to 3 weeks; 0 NOK; "no uploading microdata to third-party AI clouds" | ssb.no page logged partial; RT49's Norway row (2 to 4 weeks) has no logged page at all |
| U8 | RT51 F, E | Poland | "Access to microdata for scientific research is granted to scientific entities upon conclusion of an agreement with the President of Statistics Poland."; route via Bydgoszcz | stat.gov.pl home page, partial; RT49's Poland row (Article 38, 4 to 8 weeks) has no logged page |
| U9 | RT51 F | Greece | "Microdata files are provided to researchers for scientific purposes following the approval of the Statistical Confidentiality Committee." | ELSTAT page partial; RT49 Greece row not logged |
| U10 | RT51 F | Romania | "Access to anonymised microdata for scientific research is granted based on a written request and agreement." | insse.ro home page, partial; RT49 Romania row not logged |
| U11 | RT51 F | Hungary | "Microdata access is provided through the Safe Centre environment or remote access for registered research institutions." | ksh.hu home page, partial; RT49 Hungary row not logged |
| U12 | RT51 F | Estonia | "Statistics Estonia provides confidential data for scientific research on the basis of an application and bilateral contract." | stat.ee partial |
| U13 | RT51 F | Luxembourg | "STATEC may grant access to microdata for scientific purposes in accordance with the Law of 10 July 2011." | STATEC home page, partial |
| U14 | RT49 E, F | Serbia, Turkey | Serbia eligible, free, 4 to 8 weeks; Turkey eligible, user fee, 4 to 8 weeks | No Serbia or Turkey page in RT49's log; RT51 logged stat.gov.rs (partial) but wrote no Serbia row |
| U15 | RT51 F, E | France | "L'acces aux donnees diffusees par Quetelet-Progedo Diffusion est ouvert a toute la communaute scientifique, francaise et internationale."; 24 to 48 hours; "processed automatically"; "guaranteed to succeed immediately" | `commande.progedo.fr` is not in RT51's log. RT49 also gives 24 to 48 hours with no source |
| U16 | RT51 F | France | "Statut de diffusion: Suspendu (avlstatus: SUS). Ce fichier a ete desactive au catalogue au profit du jeu complet lil-0695." | The lil-1065 page is logged full in both RT49 and RT51, but RT49, reading the same page, reports only "avlstatus = SUS" from a JSON record and no such sentence. Unconfirmed; author to open |
| U17 | RT49 G, RT51 G | France | "Progedo suspended lil-1065 because it was a legacy subset prepared for Eurostat"; "Requesting this file causes exclusion from approved order bundles"; "approved without lil-1065 because lil-1065 is suspended ..., not because the researcher was ineligible" | No page gives a reason. The tool cannot see Progedo's decision on our request; this is a guess about our own record written as fact |
| U18 | RT49 F, RT51 S51-03 | France 2025-2026 | Fieldwork dates; "12 000 menages" quote | Insee page logged partial in all three logs. Also the URL ends `information/8212345` (a 1-2-3-4-5 run), which looks generated. Author to open |
| U19 | RT50 F | Denmark, Sweden, Switzerland | Enclave-only or "BFS contract", needs "Yes / Yes / Yes / Yes" | No logged page for dst.dk, scb.se or bfs.admin.ch |
| U20 | RT50 B11, G | Germany | "absolutely anonymised 80% subsamples"; "household and person identifiers across all four data tables"; dataset descriptions "dsb-takt, dsb-hh" | The two DOI landing pages are logged full, but the dataset descriptions named as sources are not in the log |
| U21 | RT49 B17 | MTUS | Episode file carries main, secondary activity, location, start and end times | Source "MTUS User Guide" is not in the log (the samples and terms pages are) |

Claims with a full-page log line behind them (usable for planning, still to be opened by the author before citing in a paper):
Eurostat HETUS microdata page and "How to apply" PDF (non-GDPR route, free, two steps, HETUS 2020 microdata not before 2027);
the recognised-entities list (Concordia absent; both RT49 and RT51 say 52 pages); the Progedo lil-0695 and lil-1065 records
exist; the German public-use file DOI pages exist for 2012-2013 and 2022; the German scientific-use file page (RT51, EU/EEA
only); the CBS page in RT51 ("Institutions outside the EU can only access CBS microdata if they have concluded an institutional
agreement and undergo screening."); MTUS samples page and terms PDF (cell size 30).

### 3. Contradictions across the three reports

* **HETUS 2010 countries.** RT49: 18 countries (15 EU + Norway, Serbia, Turkey); Eurostat scientific-use files for 17 (all
  but Turkey). RT51: the same 17. The arithmetic holds (15 + 2 = 17, + Turkey = 18). But RT49 Section F has no row for
  Estonia or Luxembourg (both in its own list of 17), nor for Bulgaria and Croatia (in its own list of 11 HETUS 2020 countries),
  although T49 asked for one row per country in Part 1. RT49 gives Turkey a Section F row but leaves it out of the ranking.
* **RT49 Section A counts.** "Eight countries and the centralised Eurostat ... collection are obtainable through ...
  application": Group B holds 7 countries (France, Belgium, Norway, Poland, Greece, Romania, Serbia) plus Eurostat.
  "MTUS ... across eight European countries" while B16 lists 10 (Austria, Belgium, Bulgaria, Finland, France, Hungary, Italy,
  Netherlands, Spain, UK); the 8 drop Belgium (1966) and Bulgaria (2001) without saying why.
* **Which countries are in MTUS.** Only RT49 covers MTUS (RT50 is silent, RT51 mentions it only as "verify"), so nothing
  cross-checks it. Germany and Norway are absent from MTUS per B16; Italy is 2008, not 2013-2014; Spain 2009 duplicates our
  INE file. RT49 ranks Finland, Austria and Hungary as "not obtainable" (enclave only) yet ranks MTUS "obtainable now" with
  episode files for exactly those countries. Both cannot be true unless MTUS redistributes those samples freely; the samples
  page must show whether each European sample is in the open extract or restricted.
* **Italy licence.** RT49: "Free reuse under Istat legal terms with citation". RT50: "Istat Note Legali (CC BY 3.0 IT
  equivalent)". Neither quotes the text and neither log has an Istat legal-notes page. "Equivalent" is a hedge. Not settled;
  this is a value we did not supply, so it is the diagnostic one, and it is unsourced.
* **AI and online-tool terms.** RT49 says NOT STATED for France, Belgium, Norway and Eurostat. RT51 says for the same four:
  cloud AI ingestion forbidden, local ML allowed, and (France) "model weights ... can be published". RT51 quotes no clause for
  any of them. Same answer pattern for every provider, which is template filler. Treat AI terms as unknown everywhere except
  the UK (known, clause 5).
* **Time to an answer** (none sourced except Eurostat):

| Country | RT49 | RT51 |
|---|---|---|
| France lil-0695 | 24 to 48 h | 24 to 48 h |
| Norway | 2 to 4 weeks | 1 to 3 weeks |
| Poland | 4 to 8 weeks | 3 to 6 weeks |
| Germany scientific-use file | 4 to 8 weeks | 2 to 4 weeks |
| Netherlands | 6 to 10 weeks | 6 to 12 weeks |
| Finland | 6 to 8 weeks | 4 to 6 weeks |
| Hungary | 4 to 8 weeks | 6 to 8 weeks |
| Eurostat | ~12 weeks | 12 to 14 weeks |

  RT49 gives "4 to 8 weeks" to 8 of its 21 Section F rows (Belgium, German scientific-use file, Poland, Greece, Romania,
  Hungary, Serbia, Turkey): a default, not a finding. RT49 also contradicts itself on Norway's fee ("0 NOK" in E, "Free or
  handling fee" in F). Netherlands fee: RT49 "~2,100 EUR" vs RT51 "~1,500 to 3,000 EUR + ~500 EUR/month".
* **Survey waves.** Netherlands: RT49/RT50 2011-2012 and 2021-2023, RT51 2006, 2011, 2016. Belgium: RT49/RT50 2013, RT51 2005
  and 2013. Austria: RT49 2021-2022 only, RT50/RT51 add 2008-2009. Poland: RT49/RT50 2013 and 2023, RT51 2013 only. Estonia:
  RT50 2019-2021, RT51 2020.
* **France lil-0695 contents.** Members "all 11+" (RT49, RT50) vs "all aged 10+" (RT51). The code FPR is expanded as
  "Fichier Production Recherche" (RT49) and "Fichier Pour la Recherche" (RT51); neither quotes a definition, so at least one is
  made up. One status field holding both a file type (FPR) and a state (SUS) is also odd; the author should read the page.
* **German public-use file contents.** RT49 and RT50: 10-minute diaries, all household members 10+, three diary days, weights,
  region coarsened to settlement type; RT50 adds main and secondary activity, location, household ids in all four tables and
  "80% subsamples". RT51 S51-05: the public-use file has "coarsened activity categories compared to SUF files". Open questions
  no page in any log answers: (a) whether the activity codes are full or coarsened; (b) whether the 80% subsample is drawn by
  household (households stay whole) or by person (households break); (c) whether a file anonymised enough for anyone to
  download really keeps 10-minute diaries for every member with household links. RT50's "Meets 85% of the study needs" is not
  arithmetic on four needs (one need partly met would be 3.5 of 4, 87.5%); the number is invented.
* **German public-use file status.** RT50 marks both waves `REACHED`, but also says download needs a two-step registration the
  tool did not do. By T50's own definition that is `DESCRIBED` (landing page only).
* **UK access.** RT49: "Immediate project registration ... Direct download". RT50 B14: "requiring registration and project
  application". Irrelevant to 5J (UK on hold), noted only as a consistency failure.
* **France 2025-2026.** All three say fieldwork runs October 2025 to September 2026 and call it "ongoing" or "currently in the
  fieldwork phase" on 2026-10-01, when by their own dates it has just ended. Harmless, but shows the date was not reasoned on.

### 4. Rankings that drift toward what the prompts hoped for

The prompts said the hoped-for answer: fast, free, a sole Canadian applicant, compatible with cloud-AI-assisted work, weights
shareable. Lines that deliver exactly that without a read source:
* RT51 Priority 1 (France): "guaranteed to succeed immediately", "processed automatically within 24 to 48 hours" (U15). The
  top recommendation is the case the prompt itself raised (framing inherited, vetting rule 6).
* RT51 Section A: "standard data user agreements allow running local automated Python simulation pipelines and publishing
  aggregate outputs": the study's working method, stated as a general rule with no clause quoted.
* RT51: "Sole Canadian Applicant Eligible: Yes" for France, Norway, Belgium, Poland and Eurostat; "100% compatible" or "Fully
  Compatible" for every file-delivery route. Only Eurostat's non-EU route has a full-page source.
* RT51 France: "Machine learning model weights trained on data can be published" (no source) answers the prompt's open
  question on weights in the hoped direction.
* RT49 Group B: Norway, Poland, Greece, Romania, Serbia all "Canadian eligible", "free", "file sent", none with a logged page.
* RT49 Group A is defined as "all four needs met", yet includes Germany, whose region is coarsened to settlement type by
  RT49's own text, and MTUS, whose household linkage is hedged ("where collected by the national survey").
* RT49 Group A ranks the UK "obtainable now" because terms "permit offline local execution" (see check 6).
* RT50: Germany "no restrictions on offline local AI or simulation pipelines" (no licence page read).

Lines that go against the hoped answer, which raise trust in those parts: Eurostat needs about 12 weeks, longer than the GPU
window (RT49, RT51); the German scientific-use file is closed to a non-EU sole applicant; four countries are enclave-only;
RT50 finds only three open countries. These are consistent across reports and the Eurostat and German ones have full-page
sources.

### 5. France: lil-1065 versus lil-0695 (claim for the author to check)

* Our record: Progedo request n. 38663 approved 2026-09-29 for six other files; lil-1065 not granted; France left out.
* Reports' claim: lil-1065 is "suspended" (status SUS) and cannot be ordered; lil-0695 (the national version, status FPR) holds
  the diary ("carnet", file named `EDT2010_CARNET` by RT51), is free and is granted in 1 to 2 days.
* What is supported: both records exist (two reports, logged full). What is not: the reason lil-1065 was not granted (U17), the
  French "desactive au profit de lil-0695" sentence (U16), the time, and foreign eligibility (U15).
* Why it matters: if lil-1065 was refused for a reason that also applies to lil-0695 (for example a condition on researchers
  outside France, or the producer's consent), ordering lil-0695 fails the same way.
* What would confirm it: (1) the Progedo decision on 38663 for the lil-1065 line: a stated reason of "suspendu" or
  "indisponible" supports the reports; a refusal for any other reason does not; (2) the lil-0695 page shows an order button,
  its access conditions (any condition on researchers outside France) and a diary (carnet) file in its file list; (3) the
  order itself: lil-0695 granted with a carnet file settles it.
* That the author was granted six other Progedo files shows the account can receive files; it does not show that FPR-level
  files are open to him unless those six were FPR-level too (author knows).

### 6. UK and the binding 5J rule

* **Not to be relied on, whatever its source:** RT49 Section F UK row "CD171 Section 4.5.4 exempts local offline AI"; RT49
  Section E item 4 "Terms ... permit offline local execution"; RT50 Section F UK row "CD171 exempts local offline AI". Neither
  log contains a CD171 page; RT49 says "(see RT48)", and VETTING_RT48 already marked the same sentence unverified. It is RT48's
  unsupported claim carried forward, not found again. The 5J rule (author, UKDS EUL v16 clause 5) is stricter than any such
  exemption: no AI tool ever opens UK data rows, local or cloud, until UKDS gives written permission.
* **MTUS / IPUMS:** RT49 B16 lists UK samples 1974 to 2014 in MTUS; the UK 2014 sample is built from the same UK 2014-2015
  diaries as SN 8128 (same depositor, Centre for Time Use Research). Under our rule any MTUS extract must exclude UK rows
  before any AI tool sees it; the safe way is not to select UK samples in the extract at all.
* **Eurostat HETUS 2010 scientific-use file:** its 17 countries include the UK (RT49 B3, RT51 S51-06). The same exclusion
  applies if this route is ever taken.

### 7. Other notes for the manager

* RT50 logs the Spain ZIP (`datos_emptiem0910.zip`) as opened "full" and gives an uncompressed size (~250 MB). T50 forbade
  downloading any data file. Either the tool downloaded it (a prompt breach; harmless in licence terms, Spain is CC BY 4.0) or
  the uncompressed size is invented. Compare with our held copy.
* Every "needs" column (slots, household, day, weights) reads "Yes / Yes / Yes / Yes" for countries whose pages were partial or
  unlogged, including Switzerland, which RT49 itself describes as a labour-force module "without standalone episode
  microdata". These columns are filler for every country except Spain, Italy, Germany and France.
* Germany's public-use file has no federal state, only settlement type (RT49, RT50). RT50 suggests assigning weather from
  "representative climate zones". That is a design question for the manager, not a vetting finding; noted only so it is not
  read as settled.
* The enclave exclusions (Netherlands, Austria, Finland, Hungary) agree across reports, but "EnergyPlus cannot be installed"
  is an inference no page states. Low risk: if wrong, an option is lost, nothing false enters the paper.

## For the manager

**Verdicts.** RT49 MIXED. RT50 MIXED. RT51 FAIL (salvage the route, not the table).

**Actions for the AUTHOR (ranked):**
1. **France: re-read the 38663 decision, then order lil-0695.** Check: the reason Progedo gave for lil-1065; that lil-0695 can
   be ordered, its access conditions for researchers outside France, and that its file list has a diary (carnet) file; then
   whether the order is granted and how fast. URLs: https://data.progedo.fr/studies/doi/10.13144/lil-0695 ,
   https://data.progedo.fr/studies/doi/10.13144/lil-1065 , https://commande.progedo.fr/
2. **Germany: open the public-use file pages and the variable list.** Check: 10-minute diaries for every household member with a
   household id; full or coarsened activity codes; secondary activity and location; whether the subsample is by household;
   region level; who may register from outside Germany; any rule on online or AI tools. URLs:
   https://www.forschungsdatenzentrum.de/de/10-21242-63911-2013-00-00-4-1-0 ,
   https://www.forschungsdatenzentrum.de/de/10-21242-63911-2022-00-00-4-1-1 ,
   https://www.forschungsdatenzentrum.de/de/haushalte/zve
3. **MTUS: open the terms PDF and the samples page.** Check: clauses on derived data, synthetic data, model release and online
   or AI tools; for each European sample (France 2009, Finland 2009, Austria 2008, Hungary 2009, Netherlands 2005), whether the
   episode file is in the open extract or restricted, and whether all household members are present. Never select UK samples.
   URLs: https://uma.pop.umn.edu/mtus_terms.pdf , https://www.mtusdata.org/mtus/samples.shtml ,
   https://www.mtusdata.org/mtus/terms.shtml
4. **Norway: open the SSB research-data page.** Check: whether a researcher abroad may order the 2010-2011 and 2022-2023 diary
   files, the stated time and fee, and any rule on online or AI tools (both reports' Norway facts are unsourced). URL:
   https://www.ssb.no/en/data-til-forskning
5. **Eurostat: open the HETUS microdata page and the application PDF.** Check: the non-GDPR confidentiality route for a
   Canadian institution, the stated step times, any rule on online or AI tools, and whether Concordia's research office would
   sign. UK rows would have to be excluded. URLs:
   https://ec.europa.eu/eurostat/web/microdata/collections-research/harmonised-european-time-use-surveys ,
   https://ec.europa.eu/eurostat/documents/203647/771732/How_to_apply_for_microdata_access.pdf

**Safe to state now:**
* Spain (INE 2009-2010, open, CC BY 4.0) and Italy (ISTAT 2013-2014 public-use file) are the two open files 5J uses (our own
  records; all three reports agree).
* France: the diary file lil-1065 was not granted under request 38663 (our record). A separate Progedo record, lil-0695, exists
  for the same 2009-2010 survey (two reports, logged full). Whether it can be obtained is not yet safe.
* This round found no other European country with diary microdata downloadable without an application, apart from a German
  public-use file behind a free registration. Say "none found", not "none exist".
* For internal planning only (open the page before any paper use): Eurostat gives HETUS 2010 microdata only as scientific-use
  files, free, after a two-step application open to non-EU entities; Concordia is not yet a recognised entity; HETUS 2020
  microdata are not expected before 2027; the German scientific-use file is limited to EU/EEA institutions.

**Not safe:** any eligibility, time, fee or AI-tool term for Belgium, Norway, Poland, Greece, Romania, Serbia, Turkey, Austria,
Finland, Hungary, Estonia, Luxembourg or the Netherlands' fees; the Italy licence version; MTUS household and episode content;
the German public-use file contents; the CD171 "local AI" exemption; every "guaranteed", "automatic" or "100% compatible" line.
