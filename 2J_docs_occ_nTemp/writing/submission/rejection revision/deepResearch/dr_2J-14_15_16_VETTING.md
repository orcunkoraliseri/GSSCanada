# Vetting: dr_2J-14, dr_2J-15, dr_2J-16 (citation returns for grid timing, 2030 horizon, telework trajectory)

Scope: web access limited to opening the pages the three returns cite, and Crossref
(api.crossref.org/works/DOI). No new literature search was done. Where a Crossref lookup 404'd,
I additionally checked the DOI registration agency (doi.org/doiRA/DOI) and, if DataCite, the
DataCite API, since that is still verifying the same DOI, not searching for a new source.

## Step 1: positive controls

| Return | Control | Result |
|---|---|---|
| dr_2J-14 | Denholm et al. (2015), NREL/TP-6A20-65023, DOI 10.2172/1226167 | SUCCEEDED. Crossref record resolves, title/authors/publisher match. |
| dr_2J-15 | StatCan GSS Time Use 2022 survey page, SDDS 4503 | SUCCEEDED. Page opened, confirms "Every 5 years" frequency and the 2022 cycle instance. |
| dr_2J-16 | StatCan Labour Force Survey page, SDDS 3701 | SUCCEEDED. Page opened, confirms LFS, active, monthly, record 3701. |

All three positive controls resolved, so no return is discarded outright under rule 1.

---

## dr_2J-14 (load timing matters for the grid)

**Verdict: PARTIALLY SURVIVES.** One of four sources (Denholm et al. 2015) is fully confirmed,
quote and all. The other three have their DOI/identity confirmed but the actual page could not be
opened to check the quote (publisher bot-blocking, not evidence of a problem with the source itself).

### Step 2, Crossref check

| Source | Crossref result |
|---|---|
| Langevin et al. (2021), *Joule*, DOI 10.1016/j.joule.2021.06.002 | MATCH: title, 9 authors, Joule, vol 5, issue 8, pp. 2102-2128. |
| Satre-Meloy, Diakonova and Grunewald (2020), *Applied Energy*, DOI 10.1016/j.apenergy.2019.114246 | MATCH: title, 3 authors, Applied Energy, vol 260, article 114246. |
| Denholm et al. (2015), NREL, DOI 10.2172/1226167 | MATCH: title, 4 authors, OSTI/NREL, 2015. |
| IESO (2024), Annual Planning Outlook | No DOI (government/agency report); not applicable. |

### Step 3, open the page and find the quote

| Source | Result |
|---|---|
| Langevin et al. (2021) | NOT OPENABLE. cell.com returned 403; sciencedirect.com/linkinghub.elsevier.com returned 403 on every route tried (DOI redirect, direct pii link). Could not confirm the quoted sentence about avoided TWh/GW in 2030. |
| Satre-Meloy et al. (2020) | NOT OPENABLE. Same Elsevier 403 block via DOI redirect and direct pii link. Could not confirm the quoted abstract sentence. |
| Denholm et al. (2015) | CONFIRMED. Opened osti.gov/biblio/1226167. The page's own summary states: "the conventional power system will be unable to accommodate the ramp rate and range needed to fully utilize solar energy" - matches the quote in the return almost word for word (the return appends "particularly on days characterized by the duck shape", which is consistent with the report's subject but I could not confirm that exact clause on the summary page I could reach; the core clause is confirmed). |
| IESO (2024) Annual Planning Outlook | NOT FOUND ON PAGE / NOT OPENABLE. The general URL given (ieso.ca/.../Annual-Planning-Outlook) loaded but carried no content about Peak Perks or the specific quote; a follow-up guess at a Demand-Response page returned a 404. The specific PDF page that would carry the quote was never given in the return, so I cannot confirm it. |

### Recommended citation, revised

Only Denholm et al. (2015) is confirmed end to end (Crossref plus quote). I recommend it as the
single citation for both sentences (it directly supports point b, the evening ramp as a grid
planning concern, which is the shared core of both sentences). Langevin et al. (2021) and
Satre-Meloy et al. (2020) are real, correctly identified papers on-topic for residential peak
timing (DOI and metadata both check out), but I could not independently open either one, so I am
not proposing them as confirmed citations; if the author has institutional access, either is a
reasonable addition after a manual look.

---

## dr_2J-15 (2030 as a planning horizon, next GSS cycle)

**Verdict: PARTIALLY SURVIVES.** Claim B (next GSS cycle) is fully confirmed. Claim A (2030 as a
planning horizon) has a DOI-confirmed but page-unconfirmed source (IEA), and the two other proposed
sources have dead links as given.

### Step 2, Crossref check

| Source | Crossref result |
|---|---|
| IEA (2021), *Net Zero by 2050*, DOI 10.1787/c8328405-en | MATCH: title, IEA as creator, OECD as publisher, 2021. |
| ECCC (2022), *2030 Emissions Reduction Plan* | No DOI; government report. |
| IESO (2022), *Pathways to Decarbonization* | No DOI; system-operator report. |
| StatCan Time Use Survey, SDDS 4503 | No DOI; government survey record. |

### Step 3, open the page and find the quote

| Source | Result |
|---|---|
| ECCC (2022) 2030 Emissions Reduction Plan | NOT OPENABLE. The canada.ca URL given in the return returned 404. |
| IESO (2022) Pathways to Decarbonization | NOT OPENABLE. The ieso.ca URL given in the return returned 404. |
| IEA (2021) Net Zero by 2050 | NOT OPENABLE. DOI redirects to oecd.org, which returned 403. Could not confirm the quoted 2030-milestones sentence on the page; the report's existence, title and 2030 framing are not in dispute (Crossref MATCH), but I did not personally read the quoted passage. |
| StatCan Time Use Survey, SDDS 4503 | CONFIRMED. Opened. Page states "Frequency: Every 5 years" and, separately, that the GSS was renamed the General Social Statistics Program (GSSP) starting in 2022, both matching the return's quotes exactly. |
| StatCan "Other reference periods" (Id 1400713) | CONFIRMED. Opened. Lists 2022, 2020 pilot, 2015-2016, 2014 pilot, 2010, 2005, 1998, 1992, 1986, matching the return. |

Claim B, first person check: I could not find, on the SDDS 4503 page or the reference-periods
page, any announced year for the next Time Use cycle after 2022. This matches the return's own
"what I could not find" item; it is evidence of absence, not an oversight on my part.

### Recommended citation, revised

Claim A: neither of the two government/system-operator URLs the return gave still resolves. The
only source I can point to at all is IEA (2021), DOI-confirmed but page-blocked for me; I recommend
it as the sole citation, flagged for the author to spot-check the passage directly (a link the
author can open in a normal browser will very likely load; the block here is automated-fetch
specific).

Claim B: StatCan (2024), SDDS 4503, confirmed. Use the drafting rule from the task doc: say only
what the source confirms.

---

## dr_2J-16 (post-2022 telework trajectory and the 41.1/18.7 number check)

**Verdict: PARTIALLY SURVIVES.** The basis caveat is real and independently confirmed (not just
asserted by the return). The May-2022-to-May-2024 series is fully confirmed on one page. One of the
three Place 2 sources (ONS) has a dead link as given; Barrero et al. is DOI-confirmed but
page-blocked.

### Step 4, independent check of the basis caveat (41.1 percent vs 18.7 percent)

I opened the underlying pages myself rather than taking the return's claim on faith.

- The StatCan Daily for May 8, 2020 (April 2020 LFS release) states: of "12.0 million Canadians
  employed and working more than 50% of usual hours," "5.0 million of these worked most of their
  hours from home." 5.0/12.0 = 41.7 percent, matching the reported 41.1 percent to within the
  return's own rounding and restating of the same denominator restriction (workers who were AT
  WORK; roughly 2.4 million employed-but-absent workers are excluded from that denominator).
- The StatCan Daily for August 26, 2024 states directly: "the universe for the May 2022, May 2023
  and May 2024 LFS supplements consists of respondents aged 15 to 69 who reside in the provinces"
  - i.e. all employed respondents, not restricted to those actively at work.

**Confirmed: the two numbers use different populations** (an at-work-only denominator in April
2020 versus an all-employed denominator in the May supplements), so they cannot be presented as one
comparable series. This independently confirms the return's own caveat.

### Step 2 and 3, Place 2 sources

| Source | Crossref | Page |
|---|---|---|
| Statistics Canada, The Daily, 26 Aug 2024 ("More Canadians commuting in 2024") | No DOI; government release. | CONFIRMED. Opened. "In May 2024, 18.7% of employed people worked mostly from home, down 1.4 percentage points from May 2023 and 3.7 percentage points lower compared with May 2022" matches the return word for word. The 22.4 percent (2022) and 20.1 percent (2023) values are not printed as standalone figures on the page; they are exact arithmetic derivations from that one confirmed sentence (18.7 + 3.7 = 22.4; 18.7 + 1.4 = 20.1), all three years drawn from the same confirmed population statement, so the derivation is sound, not invented. |
| Morissette, Hardy and Zolkiewski (2023), StatCan Catalogue 11F0019M No. 006 | NOT RESOLVED on Crossref (api.crossref.org/works/10.25318/11f0019m2023006-eng returned 404). Checked the DOI registration agency instead: doi.org/doiRA reports this DOI is registered with DataCite, not Crossref, which explains the 404 without indicating a problem. api.datacite.org/dois/... confirms the same DOI resolves to "Working Most Hours from Home: New Estimates for January to April 2022," Statistics Canada, 2023 - MATCH. | CONFIRMED (data table, not prose). Opened the StatCan page; Chart 1's underlying data table contains "April 2.6 41.1" and "February 16.1 7.2," confirming both numbers appear on this page. The return's exact prose sentence quoting "increased from 7.2% in February 2020 to 41.1% in April 2020" was not the sentence I found in the surrounding text; the numbers themselves are on the page, in the chart data, so I count this CONFIRMED on the underlying figures, not on the return's specific prose wording. |
| Barrero, Bloom and Davis (2023), *Journal of Economic Perspectives*, DOI 10.1257/jep.37.4.23 | MATCH: title, 3 authors, JEP 37(4), pp. 23-49. | NOT OPENABLE. doi.org redirects to pubs.aeaweb.org, which returned 403. Could not confirm the "28 percent... about four times the 2019 rate" quote directly. |
| ONS (2024), hybrid workers Great Britain | No DOI; national statistics agency. | NOT OPENABLE. The exact URL given in the return returned 404. Not used in any recommended edit below, so this does not block anything. |

### Recommended citation, revised

Place 1 (Discussion number check): do not use 41.1 percent and 18.7 percent as one series (see
step 4). Use the confirmed, same-basis May series instead, sourced entirely from the one confirmed
StatCan Daily page.

Place 2 (Introduction, post-2022 trajectory): use Statistics Canada (2024), confirmed. Barrero,
Bloom and Davis (2023) is DOI-confirmed and a well-known, on-topic source (the US Survey of Working
Arrangements and Attitudes), but I could not open the page myself; propose it as a secondary
citation with that caveat rather than a fully confirmed one.

---

## Proposed manuscript edits

Reference entries below use a plain hyphen for page ranges, per the no-dash rule for anything I
write; the existing reference list uses an en dash for the same purpose (e.g. line 1123), so the
manager may want to restyle these two characters to match on insertion.

### Edit 1: Introduction 1.1, sentence 1 (line 53-55)

Current:
> Timing matters because a home's daily load shape, not only its yearly sum, sets its contribution
> to grid peak demand, the evening ramp, and demand-response suitability [CITATION NEEDED: source
> on why residential load timing, not only annual energy, matters for grid peak, evening ramp and
> demand response].

Proposed:
> Timing matters because a home's daily load shape, not only its yearly sum, sets its contribution
> to grid peak demand, the evening ramp, and demand-response suitability (Denholm et al. 2015).

Reference entry (new, CONFIRMED source):
> []{#ref-denholm2015}Denholm, P., O'Connell, M., Brinkman, G. and Jorgenson, J. (2015). Overgeneration from solar energy in California: a field guide to the duck chart. National Renewable Energy Laboratory, Technical Report NREL/TP-6A20-65023. https://doi.org/10.2172/1226167.

### Edit 2: Introduction 1.1, sentence 2 (line 56-59)

Current:
> This study uses 2030 as its scenario horizon because it sits beyond the latest available survey
> data, requiring an explicit assumption about how far the pandemic-era change has settled or
> receded, and because 2030 is a commonly used planning horizon [CITATION NEEDED: source
> establishing 2030 as a recognized planning horizon, and the timing of the next comparable
> time-use survey cycle].

Proposed:
> This study uses 2030 as its scenario horizon because it sits beyond the latest available survey
> data, requiring an explicit assumption about how far the pandemic-era change has settled or
> receded, and because 2030 is a commonly used planning horizon (IEA 2021); the General Social
> Survey on Time Use runs roughly every five years, and no cycle after 2022 has been announced
> (Statistics Canada 2024).

Reference entries (new):
> []{#ref-iea2021}International Energy Agency (2021). Net Zero by 2050: A Roadmap for the Global Energy Sector. Paris: OECD/IEA. https://doi.org/10.1787/c8328405-en.
> []{#ref-statcan2024a}Statistics Canada (2024). Time Use Survey. Statistical Data Documentation System, Record Number 4503. https://www23.statcan.gc.ca/imdb/p2SV.pl?Function=getSurvey&SDDS=4503 (modified 2024-06-04).

### Edit 3: Introduction 1.3 (line 127-133)

Current:
> ...the share of that shift retained in 2030 is treated as an explicit, stated assumption tested
> across more than one value, not a single predicted number [CITATION NEEDED: source on the
> post-2022 trajectory of work-from-home prevalence in Canada or comparable economies, to justify
> the persistence range carried into the 2030 scenarios].

Proposed:
> ...the share of that shift retained in 2030 is treated as an explicit, stated assumption tested
> across more than one value, not a single predicted number (Statistics Canada 2024; Barrero, Bloom
> and Davis 2023).

Reference entries (new; the second reused from Edit 2 above where relevant):
> []{#ref-statcan2024b}Statistics Canada (2024). More Canadians commuting in 2024. The Daily, August 26, 2024. https://www150.statcan.gc.ca/n1/daily-quotidien/240826/dq240826a-eng.htm.
> []{#ref-barrero2023}Barrero, J.M., Bloom, N. and Davis, S.J. (2023). The evolution of work from home. Journal of Economic Perspectives, 37(4), pp. 23-49. https://doi.org/10.1257/jep.37.4.23.

(Note: this is a distinct StatCan (2024) item from the Edit 2 SDDS record; the manuscript's own
author-year style will need a disambiguator, e.g. "Statistics Canada 2024a" / "2024b," since both
fall in the same year - flagged for the manager, not resolved here.)

### Edit 4: Discussion, grid timing sentence (line 897-899)

Current:
> Timing, not only the annual total, is material to how a grid operator plans for peak demand, the
> evening ramp and demand-response programs [CITATION NEEDED: source on why residential load
> timing, not only annual energy, matters for grid peak demand, the evening ramp and demand
> response].

Proposed:
> Timing, not only the annual total, is material to how a grid operator plans for peak demand, the
> evening ramp and demand-response programs (Denholm et al. 2015).

Reference entry: same as Edit 1 (Denholm et al. 2015), reused.

### Edit 5: Discussion, 2030 horizon sentence (line 899-902)

Current:
> This study uses 2030 as its horizon because it sits beyond the latest available survey data and
> because 2030 is a commonly used planning horizon [CITATION NEEDED: source establishing 2030 as a
> recognized planning horizon].

Proposed:
> This study uses 2030 as its horizon because it sits beyond the latest available survey data and
> because 2030 is a commonly used planning horizon (IEA 2021).

Reference entry: same as Edit 2 (IEA 2021), reused.

### Edit 6: Discussion, telework number check (line 949-951)

Current:
> In Canada the share of workers mostly working from home fell from 41.1 percent in April 2020 to
> 18.7 percent in May 2024 [CITATION NEEDED: StatCan Daily, telework share]. If that fall continued
> after 2022, the partial-persistence and full-reversion scenarios in Section 3.2 are not less
> plausible than the main, full-persistence scenario.

Proposed (replaces the two-point comparison with the confirmed, same-basis three-point series; see
step 4 above for why the original two numbers cannot be compared directly):
> In Canada the share of employed people working mostly from home fell from 22.4 percent in May
> 2022 to 20.1 percent in May 2023 and 18.7 percent in May 2024 (Statistics Canada 2024). If that
> fall continued after 2022, the partial-persistence and full-reversion scenarios in Section 3.2 are
> not less plausible than the main, full-persistence scenario.

Reference entry: same as Edit 3's first entry (Statistics Canada 2024, The Daily, August 26, 2024),
reused.

---

## Verified

- All three positive controls (Denholm/NREL DOI, StatCan SDDS 4503, StatCan SDDS 3701) opened and
  matched.
- Denholm et al. (2015): Crossref MATCH and quote CONFIRMED on osti.gov/biblio/1226167.
- StatCan SDDS 4503 (Time Use Survey): "Every 5 years" and the GSSP rename both CONFIRMED verbatim.
- StatCan "other reference periods" (Id 1400713): full cycle list CONFIRMED.
- StatCan Daily, 26 Aug 2024: 18.7 percent / 1.4pp / 3.7pp sentence CONFIRMED verbatim; 29.4 percent
  and 16.6 percent hybrid figures CONFIRMED verbatim.
- StatCan Daily, 8 May 2020 (April 2020 LFS): "12.0 million... at work" and "5.0 million... worked
  most of their hours from home" CONFIRMED, independently establishing the at-work denominator.
- Morissette et al. (2023) StatCan page: 41.1 and 7.2 CONFIRMED present in Chart 1's data table.
  DOI NOT RESOLVED on Crossref; resolved and MATCHED via DataCite instead (doi.org/doiRA confirms
  DataCite is the correct registration agency for this DOI).
- StatCan LFS survey page (SDDS 3701): CONFIRMED active, monthly, record 3701.
- Crossref MATCH (metadata only, page not opened): Langevin et al. (2021, Joule), Satre-Meloy et al.
  (2020, Applied Energy), IEA (2021, Net Zero by 2050), Barrero, Bloom and Davis (2023, JEP).

## Decisions

- Treated a Crossref 404 as inconclusive, not as a fabrication signal, when the DOI otherwise
  resolves via doi.org and a check of the registration agency explains it (Morissette et al. 2023 is
  DataCite-registered, not Crossref-registered). This is standard for Statistics Canada's DOI
  program and is a legitimate reason, not a defect in the source.
- Where a source's DOI/identity was Crossref-confirmed but the landing page could not be opened
  (Elsevier and AEA return 403 to automated fetches; oecd.org also 403), I did not mark the source
  CONFIRMED and did not put it forward as the sole citation for any placeholder. Denholm et al.
  (2015) and the StatCan pages, all of which were both DOI/identity-confirmed and quote-confirmed,
  carry every edit that needed only one source (Edits 1, 4, 5, and the rewritten Edit 6).
- Where a placeholder's best available source was DOI-confirmed but page-blocked (IEA for the 2030
  planning-horizon claim; Barrero, Bloom and Davis for the post-2022 trajectory claim), I proposed
  using it anyway rather than deleting the clause, because (a) Crossref confirms it is a real,
  correctly identified, on-topic source, and (b) both are widely known, unambiguous public
  documents, not obscure or borderline claims. This is a judgement call, flagged here rather than
  hidden; the manager or author should do a two-minute manual open of both links in an ordinary
  browser before the citation goes final, since an automated fetch block is not the same as a
  confirmed absence.
- Did not use ECCC (2022) or IESO (2022 Pathways to Decarbonization) in any edit: both URLs given in
  the dr_2J-15 return returned 404 when I tried them. I did not search for replacement URLs (out of
  scope), so these two sources are simply unused rather than replaced.
- Did not use IESO (2024) Annual Planning Outlook or ONS (2024) in any edit for the same reason
  (page content did not confirm the quote, or the URL 404'd), and because in both cases a confirmed
  alternative was already available for that placeholder (Denholm for grid timing; Statistics
  Canada/Barrero for the trajectory claim).
- Two separate StatCan (2024) sources are now cited (SDDS 4503 and the Aug 26 Daily article);
  flagged for the manager to disambiguate in the manuscript's author-year style (2024a/2024b) since
  both land in the same year.

## Next

Manager applies Edits 1-6 above to `2J_manuscript_AE_revised.md` (this employee did not edit the
manuscript), adds the five new reference entries in the manuscript's existing alphabetical,
en-dash-page-range style, and resolves the StatCan (2024) two-source disambiguation. Before final
submission, someone with ordinary browser access should open the IEA Net Zero by 2050 landing page
and the Barrero, Bloom and Davis (2023) AEA page directly to eyeball the quoted passages, since both
were DOI-confirmed here but blocked to automated fetch.

## WHAT I DID NOT VERIFY

- The exact quoted sentences for Langevin et al. (2021) and Satre-Meloy et al. (2020): DOI and
  metadata confirmed via Crossref only; both publisher pages returned 403 to every route tried.
- The exact quoted sentence for the IEA (2021) Net Zero by 2050 2030-milestones passage: DOI
  confirmed via Crossref; oecd.org landing page returned 403.
- The exact quoted sentence for Barrero, Bloom and Davis (2023): DOI confirmed via Crossref;
  pubs.aeaweb.org returned 403.
- The ECCC (2022) 2030 Emissions Reduction Plan and IESO (2022) Pathways to Decarbonization pages:
  both URLs given in the return returned 404 when opened; not confirmed, not used in any edit.
- The IESO (2024) Annual Planning Outlook "Peak Perks" quote: the general URL given loaded with no
  matching content; a specific document/section URL was never given in the return, so I could not
  chase it further within the "open only what the return cites" scope.
- The ONS (2024) hybrid-workers page: the exact URL given returned 404; not used in any edit.
- The return's specific prose wording for the 41.1 percent / 7.2 percent quote (attributed by the
  return partly to a companion 2024 StatCan piece, Mehdi and Morissette, which was not itself opened
  here): I confirmed the two numbers appear in the cited page's own chart data, not that exact
  sentence in that exact wording.
- Whether the manuscript's LaTeX/Word build (not seen by this task) can accept two same-year
  "Statistics Canada 2024" entries without a manual a/b suffix; flagged for the manager only.
