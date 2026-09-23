# Vetting record: `RL36`

#### Vetted 2026-09-23, before any value entered the manuscript or any plan document.
#### Procedure: `README.md` section *Vetting a returned report, BEFORE any value enters a document* (7 steps).
#### Prompt: `L36_measured_residential_load_profiles.md` (6,455 B)
#### Response: `RL36_measured_residential_load_profiles.md` (20,004 B), returned 2026-09-23.
#### Session record: `TRANSCRIPT_NOTES_RL34_RL35_RL36.md` (RL35 and RL36 came from one session).

---

## VERDICT

| Part of the report | Verdict | Carried into our documents | Rejected |
|---|---|---|---|
| Every weekday peak hour and secondary peak (9 of 9 sources) | **REJECTED.** All asserted, none seen. | nothing | all nine "read from figure" / "read from table" cells, with their figure and table numbers |
| Source list, as a list of routes | **ACCEPTED AS ROUTES ONLY.** Three routes resolve and are worth the author's time: the IDAE SPAHOUSEC PDF, Besagni et al. (2020), the Low Carbon London data on the London Datastore. | the three routes, to be opened by the author | every household count, year range, licence and resolution attached to them |
| UK Household Electricity Survey identifier | **REJECTED.** The DOI resolves to a different study. | nothing | `10.5255/UKDA-SN-7591-1` as HES |
| Positive control (Elexon Profile Class 1) | **HALF PASS.** The one-sentence definition is plausible; both URLs given are 404. | nothing | both Elexon URLs |
| Question A (one common three-country source) | **ACCEPTED AS AN ABSENCE, weakly.** "No single comparable source" is the non-rescuing answer. Its supporting description of REMODECE is rejected: the REMODECE host does not resolve. | only as our own dated "we did not find", if needed at all | the three REMODECE reasons |
| Question C (can appliances be separated from heating) | **REJECTED.** It says yes for all three countries. That is the rescuing answer, it rests on no opened document, and the Italy argument turns whole-house data into appliance data by assertion. | nothing | all three separability claims |

**The session transcript shows no full-text PDF and no data file downloaded for any RL36 source.** The only
checkable call it made for RL36 is one Crossref title query ("Italian Household Load Profiles A Monitoring
Campaign"); the report itself was written by a script (`generate_rl36.py`) whose contents are not in the
transcript. Every "Where seen in source" cell (figure number, table number, page range) is therefore
unsupported, however specific it looks. **Nothing numeric from RL36 enters any document.**

---

## 1. Checks run, and what each returned

All checks 2026-09-23. Only DOI identity calls (Crossref, DataCite) and plain HTTP status plus title-tag
checks were made. No page content was read beyond the `<title>` tag; no search was run.

### 1.1 DOI identity checks

| DOI as given in RL36 | Registry | Title the registry returned | Match? |
|---|---|---|---|
| `10.3390/buildings10120217` | Crossref | "Italian Household Load Profiles: A Monitoring Campaign"; authors Giorgio Besagni, Lidia Premoli Vilà, Marco Borgarello; *Buildings* 10(12), article 217; issued 2020-11-27; MDPI AG | **YES.** Title, authors, journal, volume, issue and article number all match. Note the accent: Premoli Vil**à**. |
| `10.5255/UKDA-SN-7591-1` (given as the Household Electricity Survey 2010-11) | DataCite | "Energy Demand Research Project: Early Smart Meter Trials, 2007-2010" (EDRP); creator AECOM Building Engineering; UK Data Service, 2018 | **NO.** SN 7591 is the EDRP smart-meter trial, not HES. The report's "premier" UK source carries another study's identifier. |

We also tried one candidate study number for HES from our own memory (`10.5255/UKDA-SN-8209-1`). DataCite
returned a CLOSER height and weight cohort study. **Our memory was wrong too; we did not guess further.**
The correct HES study number is NOT FOUND by us, and the author must look it up by title in the UK Data
Service catalogue.

### 1.2 HTTP status of every URL the report gives

`curl -s -L -A "Mozilla/5.0"`, status code, final URL after redirects, and `<title>` only.

| URL as given | Status | Final URL / title | Reading |
|---|---|---|---|
| `https://www.idae.es/uploads/documentos/documentos_Informe_SPAHOUSEC_ACC_f68291a3.pdf` | 200 | same URL; `application/pdf`, 4,002,118 bytes, last modified 2022-11-14 | **Resolves to a real PDF.** Contents not read by us. |
| `https://www.esios.ree.es/es/mercados-y-precios/perfiles-de-consumo` | 200 | title "Esios Red Eléctrica" | **Proves nothing.** A made-up path on the same site (`/es/zzz-nonexistent-page-xyz`) also returns 200 with the same title. ESIOS is a single-page app that answers 200 to every path. |
| `https://datadis.es` | 200 | title "Datadis" | Home page only. The prompt asked for the page where the numbers are. |
| `https://doi.org/10.3390/buildings10120217` | 403 | redirects to `https://www.mdpi.com/2075-5309/10/12/217`, title "Access Denied" | DOI resolves to the right article path; MDPI blocks scripted clients. Open in a browser. |
| `https://www.e-distribuzione.it` | 200 | title "E-Distribuzione: distribuzione e misura di energia elettrica" | Home page only. No data file or table URL given. |
| `https://www.arera.it/atti-e-provvedimenti/dettaglio/09/107-09` | **404** | same URL | **Does not resolve.** |
| `http://www.eerg.polimi.it` | 200 | redirects to https; title "eERG, end-use Efficiency Research Group, Politecnico di Milano" | Home page only. No MICENE document URL given. |
| `https://doi.org/10.5255/UKDA-SN-7591-1` | 200 | `datacatalogue.ukdataservice.ac.uk/studies/study/7591` | Resolves, **to EDRP, not HES** (see 1.1). |
| `https://bscdocs.elexon.co.uk/guidance-note/load-profiles-and-their-use-in-electricity-settlement` | **404** | same URL | **Does not resolve.** This is the report's main Elexon URL and its positive-control URL. |
| `https://www.elexon.co.uk/knowledgebase/profiling/` | **404** | redirects to `/bsc/knowledgebase/profiling/`, title "Page not found - Elexon BSC" | **Does not resolve.** The second positive-control URL. |
| `https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households` | 200 | redirects to `.../smartmeter-energy-consumption-data-in-london-households-vqm0d`, title "SmartMeter Energy Consumption Data in London Households, London Datastore" | **Resolves**, under a renamed slug. Title matches the claimed dataset. |
| `http://remodece.isr.uc.pt/` | none | curl exit 6 (host name does not resolve), for both http and https | **Host does not exist in DNS today.** |

**Tally: 12 URLs. 3 are 404, 1 host does not exist, 4 are home pages only, 1 is a single-page app whose
200 means nothing, 1 is a DOI for the wrong study. Three resolve to what they claim: the SPAHOUSEC PDF, the
Besagni DOI, the London Datastore page.**

### 1.3 Every "where seen" cell is unsupported

The prompt's rule was: a peak hour only from a table or figure actually seen, with its number; otherwise
NOT SEEN. RL36 fills the "Weekday peak hour" and "Where seen in source" cells for **all nine** sources,
with figure numbers, table numbers and page ranges (for example "Grafico 4.12 ... pp. 54-58", "Figure 6 ...
Figure 8 (pp. 8-11)", "Figure 9 ... p. 31"). It writes NOT SEEN **zero** times. The transcript shows no
full-text or data-file retrieval for any RL36 source. Two of the "seen" sources (REMODECE, the Elexon
guidance note) cannot even be reached today. This is README vetting step 3 exactly: the provenance column
gives the round away before any value is examined.

### 1.4 The peak hours are copied across sources within each country

| Country | Three sources of different kind | Peak hours returned |
|---|---|---|
| Spain | appliance-only sub-metering (2010-11); whole-house settlement profile with heating and air conditioning, mixed with small business (2021 on); aggregated smart meters | **21:00-22:00 evening and 14:00-15:00 midday, identical in all three** |
| Italy | monitoring panel (2018-19); settlement profile; appliance sub-metering (2000s) | 20:30-21:30, 20:00-21:00, 20:00-21:30; midday 12:30-13:30, 12:00-13:00, 12:30-13:30 |
| UK | appliance sub-metering (2010-11); settlement profile; smart-meter trial (2011-14) | 18:00-19:00 in all three |

Three populations, three measurement bases, three decades, and the same hour to the hour in Spain. An
appliance-only curve and a whole-house curve that includes electric heating and summer air conditioning
need not peak at different hours, but agreement this exact across every source reads as one asserted value
written into three cells.

### 1.5 Settlement-period arithmetic (an identity it cannot fake)

GB settlement period *n* covers the half-hour starting at (*n* - 1) x 30 minutes after midnight. So period
36 is 17:30-18:00 and period 37 is 18:00-18:30. The Elexon row says "Half-hour 36-37 (18:00-18:30,
extending across 18:00-19:00)". **Periods 36-37 span 17:30-18:30, not 18:00-18:30.** The Low Carbon London
row ("Half-hour 37 (18:00-18:30)") has it right, so the error is inside one document. Small, but it is the
kind of detail a report that had read the table would not get wrong.

### 1.6 Claims the report could not have observed

* **REMODECE**: "The public web database hosted by ISR-Coimbra (`http://remodece.isr.uc.pt/`) is currently
  largely archival and provides static annual consumption averages". The host does not resolve. "Currently"
  was not observed. Its other two REMODECE reasons (UK data "retrofitted from Energy Saving Trust data";
  two-week campaigns) and its claim that REMODECE covered all three of our countries are uncheckable here
  and rest on nothing opened.
* **Datadis**: a public page named "Curva de carga media horaria por provincia y tarifa 2.0TD" is quoted as
  where the peak was "read from figure", but no URL for it is given, and in the same row access is "Free
  access upon registration". From our own understanding (not checked online here) Datadis is mainly a
  portal where a supply-point holder reads their own meter data; a public aggregated provincial curve is
  not something we can confirm.
* **ESIOS "Indicator 522"**: named as the source table; not given as a URL; the page URL given cannot be
  distinguished from a nonexistent page (1.2).
* **ARERA reference**: the reference list titles Delibera ARG/elt 107/09 as the "TIT" (transmission,
  distribution and metering tariffs). From our own recollection, not checked online here, ARG/elt 107/09
  is the settlement text (TIS). The author should confirm before citing it for anything. "Delibera 237/04"
  as the origin of the household profiles is likewise unverified.
* **HES report**: "Zimmermann et al. (2012), Intertek Report R66141" is given with no URL and no DOI, and
  its author list (including "Forest, V.") is unchecked. The dataset DOI it is attached to is EDRP (1.1).

### 1.7 A prompt echo

The Elexon row says Profile Class 1 is "updated annually (including 2014-2015 HETUS period)". The report
has no reason to know or care about the HETUS period except that the prompt named the UK diary years. It
is an echo, harmless here, and a sign of how the table was filled (README vetting step 1).

---

## 2. Per-source table

"Type supported" means: is the claimed kind (measured, settlement, survey with metering, modelled)
supported by anything we could check today, not whether it is plausible.

| # | Source (as named in RL36) | Resolves? | Type as claimed, supported? | Weekday peak hour: seen or asserted | Usable for our appliance-timing comparison? | Verdict |
|---|---|---|---|---|---|---|
| 1 | IDAE SECH-SPAHOUSEC (2011), Spain | **Yes.** PDF, 200, 4.0 MB | Claimed survey with appliance sub-metering, 600 metered homes. **Not checkable** without opening; plausible from the study's known scope. | **Asserted** (Grafico 4.12 and 4.14, pp. 54-58, unseen) | **Potentially the best Spain source**: years 2010-11 sit next to our 2009-10 diaries, and if the curve is appliance-only it is the right quantity. Depends on whether the PDF actually prints an hourly weekday appliance curve, and whether as a table or only as a figure. | **ACCEPT AFTER AUTHOR DOWNLOADS** |
| 2 | REE e-sios / CNMC perfiles de consumo iniciales, 2.0TD (and older 2.0A), Spain | **Unknown.** The given page returns 200, but so does any path on that site | Settlement profile: plausible and it is what these profiles are for. "Indicator 522", the sample basis (UNESA, RD 2017/1997) and the 15-minute claim are **not checkable** here | **Asserted** ("read from table", no table seen) | **Secondary only.** Whole-house, includes electric heating, water heating and air conditioning, and covers all customers under 15 kW, not households only. 2.0TD starts 2021, eleven years after our diaries; the older 2.0A profile for about 2010 would be the fairer year if the author can get it. | **ACCEPT AFTER AUTHOR DOWNLOADS** (as a labelled settlement profile, not as household appliance demand) |
| 3 | Datadis, Spain | Home page only | Claimed aggregated smart-meter portal; **not supported**; the named public page has no URL | **Asserted** | Not as given. Whole-house even if it exists. | **REJECT** |
| 4 | Besagni, Premoli Vilà and Borgarello (2020), *Buildings* 10(12) 217, Italy | **Yes.** Crossref title and authors match; DOI redirects to the right MDPI article, which blocks scripts (403) | Claimed "RSE smart-meter and sensor panel, 50 households, 2018-2019". **Not checkable**: the session did a Crossref title query only, no full text. The report itself calls it both "smart-meter" and "high-resolution power transmitters". | **Asserted** (Figures 6 and 8 unseen) | **Probably the best Italy candidate**, but unknown until read: household count, years (2018-19 would be about five years after our 2013-14 diaries), whole-house or appliance, weekday split, and whether the data are published with it. | **ACCEPT AFTER AUTHOR DOWNLOADS**. Citation metadata ACCEPTED (with the accent). |
| 5 | e-distribuzione / ARERA standard household withdrawal profiles, Italy | e-distribuzione home page only; **ARERA URL 404** | Settlement profile: plausible in kind. The table name, the Delibera numbers and the reference title are **not supported** (1.6) | **Asserted** ("read from table") | Whole-house, includes heating; the report itself says most Italian points settle on real meter data, so the synthetic profile is a residual tool. Weak. | **REJECT as given** (the route may exist; the report did not give one we can walk) |
| 6 | MICENE, Pagliano et al. (2006), eERG Politecnico di Milano, Italy | eERG home page only | Claimed appliance sub-metering, 110 households, 2003-2005. **Not supported**: no document URL, no DOI | **Asserted** (Figure 3, Table 2 unseen) | Would be appliance-level if real, but about ten years before our Italian diaries. | **REJECT as given** |
| 7 | Household Electricity Survey 2010-11 (HES), UK | **DOI resolves to the wrong study** (EDRP, SN 7591) | Appliance sub-metering of 250 English households is the survey's known design, but **nothing the report cites supports it**: its only identifier is another dataset | **Asserted** (Figure 4 p. 22, Figure 9 p. 31, unseen) | **Yes in principle**: the only UK source where appliances and lighting can be separated from heating. Needs UK Data Service registration and the correct study number, which we did NOT FIND. | **REJECT the identifier. Route: ACCEPT AFTER AUTHOR DOWNLOADS** once the study number is found by title |
| 8 | Elexon Profile Class 1, UK | **Both URLs 404** | Settlement profile of domestic unrestricted customers: **the definition is plausible** (positive control half pass). "About 2,500 customers, Load Research Programme" not checkable. | **Asserted**, and the settlement-period label is wrong (1.5) | Whole-house, includes heating; national, not appliance-only. Useful only as a secondary, labelled check. | **REJECT the URLs. Route: ACCEPT AFTER AUTHOR DOWNLOADS** (author finds the profile coefficient files on elexon.co.uk directly) |
| 9 | Low Carbon London smart-meter data, London Datastore, UK | **Yes**, via a renamed slug; title matches | Measured household smart-meter data: **supported by the dataset title**. 5,567 households, 2011-2014, half-hourly and OGL v2.0 are asserted, not checked | **Asserted** (UKPN report Figure 3.2, no URL for that report) | **Yes, and we can compute it ourselves.** Whole-house, so any electric heating is in it; London only; years 2011-14 sit next to our 2014-15 UK diaries. | **ACCEPT AFTER AUTHOR DOWNLOADS** (best UK route we can execute ourselves) |
| 10 | REMODECE (2008), cross-country | **Host does not exist** (DNS) | Not checkable. Country coverage not checkable. | n/a (the report gives none; it says no hourly files exist) | No usable common source was shown. | **REJECT the description.** The "no common source" conclusion survives only as our own weak absence. |

---

## 3. Recommended route per country

What the author should actually download, and what we would compute from it. All URLs below returned 200
on 2026-09-23 unless marked. Nothing is computed until the file is on our disk and the relevant page or
column has been read by us.

### Spain

1. **Primary: IDAE SPAHOUSEC final report (PDF, 4.0 MB).**
   `https://www.idae.es/uploads/documentos/documentos_Informe_SPAHOUSEC_ACC_f68291a3.pdf`
   Open chapter 4 (the report claims pp. 54-58, Grafico 4.12 and 4.14). Record: does an hourly daily load
   curve for appliances (or appliances plus lighting) exist; weekday, weekend or all days; which season;
   figure only or also a table of values. **Compute:** if hourly values are printed, the weekday hour of
   the maximum, the secondary peak, and each hour's share of the daily total; if only a figure exists, the
   peak hour read from the figure, labelled "read from Grafico N", and no shape metric.
2. **Secondary: REE initial consumption profiles (perfiles iniciales).** Start at
   `https://www.esios.ree.es/` and find the profile download by hand; the path RL36 gave cannot be
   verified by status code. Prefer the 2.0A profile for a year near 2010 over 2.0TD (2021 on).
   **Compute:** mean weekday hourly shape by month, peak hour, using spring and autumn months to limit
   heating and air-conditioning influence. Label it everywhere as a settlement profile of total demand for
   all customers under 15 kW, not household appliance demand.

### Italy

1. **Primary: Besagni, Premoli Vilà and Borgarello (2020).** `https://doi.org/10.3390/buildings10120217`
   (open in a browser; MDPI refuses scripts). Record: number of households, monitoring years, whole-house or
   appliance-level, day types, whether hourly values or the underlying data are published. **Compute:**
   weekday peak hour and hourly shares, from a table or data file if one exists, otherwise the peak hour
   read from the named figure.
2. **No verified fallback.** The e-distribuzione, ARERA and MICENE routes were given as home pages or
   dead links. If Besagni et al. turns out to be unusable, **Italy is NOT FOUND**, and the manuscript says
   so rather than borrowing a profile from another country.

### United Kingdom

1. **Primary (we compute it ourselves): Low Carbon London smart-meter data.**
   `https://data.london.gov.uk/dataset/smartmeter-energy-consumption-data-in-london-households-vqm0d`
   Download the half-hourly files. **Compute:** keep the standard-tariff households only (the time-of-use
   group had prices that shift the peak by design); mean weekday half-hourly profile over a full year and
   over spring and autumn months; peak half-hour, secondary peak, hourly shares. Label as measured
   whole-house demand, London, heating included. The full release is large, so any processing runs as a
   Speed batch job, not locally or on the login node.
2. **Secondary (appliance-separable): Household Electricity Survey 2010-11.** Find it by title in the UK
   Data Service catalogue (`https://datacatalogue.ukdataservice.ac.uk/`); **SN 7591 is NOT it** (that is
   EDRP). Registration and an end-user licence are needed. **Compute:** weekday appliance-plus-lighting
   profile with space heating, water heating and showers removed; peak hour and shares.
3. **Tertiary: Elexon Profile Class 1 coefficients.** Find the profile download on `https://www.elexon.co.uk/`
   by hand; both URLs RL36 gave are 404. **Compute:** weekday peak settlement period by season, labelled as
   a whole-house settlement profile.

**Across all three countries**, only the UK has a route that is both measured and computable by us today
(Low Carbon London). Spain and Italy each depend on one document that nobody has opened yet. The three
checks will not be on one basis: expect one appliance-level curve (Spain, if SPAHOUSEC delivers), one of
unknown kind (Italy) and one whole-house curve (UK). The comparison must say which is which.

---

## 4. What may enter the manuscript now

**Nothing numeric.** No peak hour, secondary peak, household count, year range, resolution or licence
from RL36 may be written anywhere.

* Bibliographic entry only: **Besagni, G., Premoli Vilà, L., Borgarello, M., 2020. Italian household load
  profiles: a monitoring campaign. Buildings 10 (12), 217. https://doi.org/10.3390/buildings10120217**
  (Crossref-checked 2026-09-23). It may be cited only after the author has read it and it supports the
  sentence it is attached to.
* **No other RL36 citation is fit for a bibliography today.** The HES citation carries the wrong dataset
  identifier; the Elexon and ARERA entries carry dead URLs; MICENE and the Intertek report have neither
  URL nor DOI.
* An absence, if the paper needs one at all, only in the first person and dated: *"we did not find a
  single published source giving comparable measured household profiles for Spain, Italy and the United
  Kingdom (search of 2026-09-23)"*. RL36's reasons for it are not to be repeated.
* **Warning for when real numbers arrive.** RL36 gives Spain a 21:00-22:00 main peak and a 14:00-15:00
  secondary peak. Our modelled Spanish appliance peak is 14:00. It would be easy to match our value to the
  source's **secondary** peak and call it agreement. Decide before opening any file which peak (the daily
  maximum) is compared, and report a mismatch as a mismatch.

---

## 5. Round-level verdict against the README's seven steps

| Step | Result |
|---|---|
| 1. Check its claims about our own work first | **PASS, with one echo.** It made no claims about our model; the "2014-2015 HETUS period" phrase in the Elexon row is copied from the prompt (1.7). |
| 2. Agreement with what we supplied tells us nothing | **MOSTLY ECHO.** Eight of its ten sources are the prompt's own named leads, returned as findings. The one specific new item is the Besagni et al. (2020) citation, and its metadata is correct. |
| 3. Check metadata columns, not value columns | **FAILED.** Nine of nine "where seen" cells filled with figure and table numbers, zero NOT SEEN, no full text retrieved (1.3). Of 12 URLs, only 3 resolve to what they claim (1.2). |
| 4. Make it obey an identity it cannot fake | **FAILED.** The HES DOI is another study (1.1); the settlement-period label is wrong (1.5); two of three positive-control items (the URLs) are dead. The Besagni DOI passes. |
| 5. Version and date rot | **FAILED on URLs.** Both Elexon pages and the ARERA page are 404 today, the REMODECE host is gone, the London Datastore slug has changed. Every URL above carries the date 2026-09-23. |
| 6. Expect the answer to inherit the prompt's framing | **FAILED.** The prompt wanted appliance timing; the report made every country's best source appliance-separable, including Italy by arguing that gas heating makes whole-house data appliance data. |
| 7. Recommendations moving in the rescuing direction | **FAILED on Question C, PASSED on Question A.** "Every country has a usable measured source, and all three let you separate appliances from heating" is the rescuing answer, and it rests on nothing opened. Against that, its "no common three-country source" is the non-rescuing answer. Its peak hours, if taken at face value, would disagree with our model for Spain and the UK, which is also non-rescuing, but they are unseen and carry no weight either way. |

**Four of seven steps failed outright. The round is still worth keeping for three walkable routes:** the
SPAHOUSEC PDF, the Besagni et al. article and the Low Carbon London files. What failed is everything it
said it saw. What survives is where to look.

---

## 6. Actions

1. **No value from RL36 enters any document.** Every peak hour is re-derived by us from a file on our disk,
   or not used.
2. The author downloads, in this order: the SPAHOUSEC PDF, the Besagni et al. (2020) article, the Low
   Carbon London files. Each is read against the checklist in section 3 before anything is computed.
3. The HES study number is looked up by title in the UK Data Service catalogue. SN 7591 is struck
   everywhere it appears.
4. Italy is written as NOT FOUND if Besagni et al. does not deliver a weekday profile; no fallback is
   borrowed from RL36.
5. Before any file is opened, the comparison rule is fixed: the daily maximum hour is compared, per
   country, with its basis (appliance-level or whole-house) stated next to it.
