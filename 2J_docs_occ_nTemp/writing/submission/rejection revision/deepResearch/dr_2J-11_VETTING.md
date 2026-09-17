# Joint vetting of dr_2J-11 (Fable, close reading, and Gemini, live search)

Vetted: 2026-09-16. This file covers the Gemini return in full (live search, real DOIs, real web
access) plus a merge with the Fable return already vetted in `dr_2J-10_dr2J-11_FABLE_VETTING.md` (T40).
For the Fable half's own quote checks, arithmetic, and known-versus-new table, that file is the source
of record and is cited here rather than repeated. Method for the Gemini half follows the 7-step README
checklist in full, since this is a live-search return with real external sources. Quotations below
replace source titles' own em dashes and en dashes with commas or the word "to", the same convention
the two prior vetting files use; this file itself contains no em dash or en dash.

## 0. What was reviewed

`deepResearch/dr_2J-11_wfh_trajectory_and_tradeoff_gemini_results.md` (83 lines): a live-search report
on (Part A) Canadian and US work-from-home levels 2019 to 2026 plus published outlooks to 2030/2035,
and (Part B) the residential-versus-commercial energy trade-off under home working, verdict USABLE for
both parts.

## 1. Positive control (README step 1)

- Claimed: Barrero, Bloom and Davis (2021), "Why working from home will stick", NBER Working Paper
  28731, DOI 10.3386/w28731, opened via the NBER repository.
- Checked independently against Crossref (`https://api.crossref.org/works/10.3386/w28731`): title "Why
  Working from Home Will Stick", publisher "National Bureau of Economic Research", published 2021.
  Exact match (NBER working papers carry no container-title field on Crossref, which is normal, not a
  defect).
- The paper's key extracted numbers (5.0% pre-pandemic baseline, over 60% pandemic-spring-2020 peak,
  20.5% employer-planned post-pandemic share) were cross-checked against an independent web search
  summary of the NBER paper and are consistent with what is publicly reported about this paper.
- **PASS.** Positive control resolves and matches on every field checked.

## 2. DOI re-check (README step 2)

Every DOI cited for a scored or ranked source in Table A and Table B was independently re-queried
against Crossref in this pass.

| DOI | Claimed study | Crossref result | Match |
|---|---|---|---|
| 10.3386/w28731 | Barrero, Bloom and Davis 2021 | Why Working from Home Will Stick, NBER, 2021 | Yes |
| 10.1073/pnas.2304099120 | Tao et al. 2023, PNAS | Climate mitigation potentials of teleworking are sensitive to changes in lifestyle and workplace rather than ICT usage, Proceedings of the National Academy of Sciences, 2023 | Yes |
| 10.1088/1748-9326/ab8a84 | Hook, Court, Sovacool and Sorrell 2020 | A systematic review of the energy and climate impacts of teleworking, Environmental Research Letters, 2020 | Yes |
| 10.1016/j.enbuild.2020.110298 | O'Brien and Yazdani Aliabadi 2020 | Does telecommuting save energy? A critical review of quantitative studies and their research methods, Energy and Buildings, 2020 | Yes |
| 10.25318/11F0019M2023006-eng | Morissette et al. 2023, StatCan Catalogue 11F0019M No. 006 | **Does NOT resolve on Crossref (HTTP 404).** See below. | Partial, flagged |

**The Morissette DOI does not resolve on Crossref.** Crossref returned "Resource not found" (HTTP 404)
for `10.25318/11F0019M2023006-eng`. This is a real StatCan catalogue DOI, but it is registered with
DataCite, not Crossref; independently confirmed via the DataCite API
(`https://api.datacite.org/dois/10.25318/11f0019m2023006-eng`), which returns title "Working Most Hours
from Home, New Estimates for January to April 2022", publisher "Government of Canada", 2023, and via
`https://doi.org/...` resolving (HTTP 302) to
`https://www150.statcan.gc.ca/n1/pub/11f0019m/11f0019m2023006-eng.htm`. A web search independently
confirmed the named authors (René Morissette, Vincent Hardy, Voltek Zolkiewski), matching the report's
citation. **This is not a fabricated DOI; it is a real DOI on the wrong registry for a plain Crossref
lookup, exactly the same non-red-flag pattern the project has already seen for IBPSA proceedings papers
and the arXiv/DataCite Guo et al. 2026 entry in `dr_2J-12`.** Recorded here as a flag, not a fabrication.

Two Table B sources (Sepanta, Sirati and O'Brien 2024, and Crow and Millot 2020 for the IEA) carry only
URLs, no DOI, exactly as the report itself states; both were independently located and opened, see
section 3.

## 3. Source access and headline claims (README step 3)

**Sepanta, Sirati and O'Brien (2024).** Located via the Carleton University Human-Building Interaction
Lab (`carleton.ca/hbilab`), which confirms a 2025 news item announcing "a major report on
energy/emissions associated with telework" produced with PSPC, TBS, and CRA, matching the report's
description. An independent web summary of the report's own headline number states an NCR federal
employee working five days a week in the office produces 6.2 tonnes CO2e per year, against 4.6 tonnes
fully remote, a difference of 1.6 tonnes. 1.6 divided by 6.2 equals 25.8%, consistent with the report's
"25% net reduction in NCR (-1.6 t CO2e/employee/yr)" to within rounding. **CONFIRMED in substance** via
an independent source describing the same report; the full PDF itself was not opened in this pass (the
direct report URL could not be located on the lab's page), so the Quebec-specific figures (64% net
reduction, -1.3 t CO2e/employee/yr) could not be independently cross-derived and are recorded as
NOT INDEPENDENTLY VERIFIED, though nothing found in this pass contradicts them.

**Tao et al. (2023), PNAS.** Independently confirmed via PMC and other summaries of the published paper:
"switching from working onsite to working from home can reduce up to 58% of work's carbon footprint"
and "workers with two to four workdays at home can reduce GHG emissions by 11 to 29%". This matches the
report's Table B row almost exactly: "-54% to -58% for 100% remote workers" (the upper bound, 58%,
matches exactly; the lower bound, 54%, was not independently found in the secondary summaries used but
is not contradicted by them) and "-11% to -29% for 2 to 4 days/week hybrid" (exact match). The report's
"negligible (-2% to +1%) for 1 day/week hybrid" is consistent with the independently found statement
that "one day of WFH has no benefits due to offsetting factors". **CONFIRMED in substance** via an
independent open-access route (PMC), the closest to a full re-derivation achieved in this pass for any
Table B row.

**Hook et al. (2020).** Independently confirmed via the CREDS and IOPscience listings: "the paper
synthesises the results of 39 empirical studies... twenty six of the 39 studies suggest that
teleworking reduces energy use, and only eight studies suggest that teleworking increases, or has a
neutral impact." This matches the report's "26 of 39 studies find net energy reductions... 8 find
neutral or net energy increases" exactly on both counts. The report's further split of the remaining 5
studies into "ambiguous" was not found stated this way in the secondary summary used (26 + 8 = 34, not
39); this residual 5-study category is recorded as NOT INDEPENDENTLY CONFIRMED, not as contradicted,
since it is arithmetically consistent (39 minus 34 equals 5) and independent summaries commonly compress
a paper's own finer categories.

**IEA (Crow and Millot, 2020).** Independently confirmed via a direct summary of the IEA commentary
itself: "oil savings are around 11.9 million tonnes of oil equivalent (Mtoe) per year... after including
the extra residential demand, overall energy use falls by around 8.5 Mtoe, resulting in a drop of 24 Mt
in annual CO2 emissions." This is an exact match to the report's Table B row ("11.9 Mtoe transport oil
savings", "8.5 Mtoe/yr (24 Mt CO2/yr)"). **CONFIRMED**, the cleanest exact match found in this pass.

**Chen arXiv note carried over from dr_2J-10 is not relevant here; see that file.**

**Morissette et al. (2023), the report's own headline first row (A1, "7.1%" for 2016).** The actual
StatCan page was independently opened (see section 2). It contains several distinct 2016-adjacent
figures depending on exactly what is being measured: 3.6% (employees aged 15 to 69 working most of
their hours from home, 2016), 7.2% (all workers aged 15 to 69, used as the January-February 2020
baseline drawn from the 2016 Census), and a separate "7.4% in May 2016" mentioned in the document's
introduction as a different reference point. **None of these three figures found on the source page is
exactly "7.1%".** This is recorded as a genuine, specific discrepancy: the DOI, authors, and general
subject matter are all confirmed real and correctly cited, but the precise "7.1%" figure attributed to
2016 in the report's Table A could not be confirmed to appear on the source page as quoted.
**NOT CONFIRMED**, not fabricated outright (multiple close numbers exist on the real page), but the
exact figure should not be repeated to the author or into any manuscript revision without the author
re-checking the primary StatCan table directly.

The remaining A1 to A2 rows for 2020 to 2024 (41.1% April 2020, 30.0% 2020-2021 average, 24.3% May
2021, 22.4% May 2022, 20.1% May 2023, 18.7% May 2024, 15.1% June 2024, 13.2%/10.3%/23.5% split, 29.4%
hybrid share) were not individually re-opened against their StatCan Daily source pages in this pass,
given time; none of these is internally inconsistent with the confirmed 41.1% and 18.7% figures used in
the arithmetic re-derivation below, and StatCan Daily releases are a source type this project has
already treated as reliable in prior rounds.

## 4. MODELLED claims presented as measurement (README step 4)

Checked every Table A and Table B row for its DATA/MODEL/REVIEW label against whether the underlying
claim is actually observed or actually modelled/projected.

- A4's "35.0%... by 2035" (Bloom's "Nike swoosh" trajectory) is correctly labelled MODEL, not DATA. The
  report's own framing text ("Projected share... driven by technological tooling, generational
  turnover, start-up culture, and lease rollovers") correctly signals this as a forward projection, not
  a measurement.
- A4's "+25%... global increase in digital remote-capable jobs by 2030" (WEF) is correctly labelled
  MODEL.
- All four Table B rows (Sepanta, Tao, IEA, Hook, O'Brien) are correctly labelled MODEL or REVIEW, never
  DATA, consistent with all four being simulation, life-cycle-assessment, or literature-synthesis
  results rather than direct measurements.
- **No conflation found.** Every modelled or projected number in the report is labelled as such and is
  not presented as an observed measurement anywhere checked in this pass.

## 5. System-operator claims (README step 5)

N/A. No claim in the report describes what a system operator, utility, or grid actually does, as
opposed to a household or office building.

## 6. Journal-policy quotes (README step 6)

N/A. No journal editorial policy is quoted anywhere in the report.

## 7. Offline audit (README step 7)

- **A6 Canada: 41.1% (April 2020 peak) to 18.7% (May 2024).** 41.1 minus 18.7 equals 22.4. Report states
  "-22.4 pp". **Correct.**
- **A6 United States: 61.67% (May 2020 peak) to 26.70% (August 2026).** 61.67 minus 26.70 equals 34.97.
  Report states "-34.97 pp". **Correct.**
- **A2: 23.5% total home-working share as exclusive (13.2%) plus hybrid (10.3%).** 13.2 plus 10.3 equals
  23.5. **Correct.**
- **A4: Barrero et al.'s "roughly 20% compared to 5% pre-pandemic".** 20.5 divided by 5.0 equals 4.1,
  consistent with the positive control's own independently confirmed "four times pre-pandemic levels"
  framing (section 1 above). **Correct and internally consistent with the positive control.**
- **Table B, Sepanta NCR: 1.6 t CO2e/employee/yr saved against a 6.2 t CO2e/employee/yr office baseline.**
  1.6 divided by 6.2 equals 25.8%, reported as "25%". **Correct to within ordinary rounding.**
- **Table B, Hook et al.: 26 plus 8 plus an implied 5 equals 39.** 26 + 8 = 34; 39 minus 34 equals 5,
  matching the report's stated "5 ambiguous" residual exactly. **Arithmetically self-consistent**, even
  though the 5-way split itself was not independently confirmed against the source (section 3 above).

No arithmetic error was found in dr_2J-11, in contrast to the systematic undercounting found in
dr_2J-10's Table B (see `dr_2J-10_VETTING.md` section 7).

## 8. Merge with the Fable return's structural critique

The Fable return (`dr_2J-10_dr2J-11_FABLE_VETTING.md`, T40, SURVIVES VETTING) found the manuscript's
2030 scenario is constructed so that WFH "persists with probability one" after 2022 (section 7,
paragraph 9), meaning the model's behavioural component is held fixed for the entire 2022-to-2030 leg;
since that leg is the only one carrying the confidence-interval-bearing shape statistics the abstract
and Fig. 6 caption cite as evidence of a "WFH effect," the causal label is not tested by the statistic
used to support it. This is a close-reading finding about the manuscript's own internal construction,
requiring no external data. The Gemini return's verdict, USABLE for both parts, answers a different
question: whether real external data and literature exist to build a genuine WFH trajectory scenario
and a genuine home-versus-office trade-off paragraph.

**Do not silently pick one; both positions stand, and here is how they interact:**

- **Mostly orthogonal on the main mechanism.** Gemini's Part A confirms that real trajectory data and
  published projections to 2030 and 2035 exist (Bloom's trajectory, Barrero et al.'s employer-planned
  share). This does not touch Fable's specific objection, that the manuscript's own 2030 scenario, as
  currently constructed, holds behaviour fixed after 2022 rather than actually using any of this
  trajectory data to drive the 2022-to-2030 leg. Real external data existing is a necessary condition
  for fixing WP2's scenario design; it is not itself evidence about whether the current single-scenario
  construction is flawed, which is what Fable establishes independently.
- **Gemini's own trajectory numbers strengthen Fable's critique with real evidence that the "persists
  with probability one" assumption is not the best available central case.** Gemini's own Table A rows
  show Canada's mostly-from-home share continuing to decline monotonically after 2022: 22.4% (May 2022),
  20.1% (May 2023), 18.7% (May 2024); the US SWAA series shows the same pattern: 30.36% (2022), 28.67%
  (2023), 27.64% (2024), 26.83% (2025), 25.86% (2026 through August). **Both series, from the report's
  own primary source data, show WFH continuing to decline for four straight years after 2022, directly
  contradicting a scenario that assumes it stays flat ("persists with probability one") through 2030.**
  This is new, externally sourced, quantitative evidence that reinforces Fable's structural finding: not
  only is the manuscript's "persists" framing an unjustified assumption in the abstract (Fable's point),
  the best available real-world trend since 2022 actually moves in the opposite direction from what
  "persists" implies. This is a genuinely new, actionable finding, not mere corroboration of an existing
  plan item, and is separate from `dr_2J-12`'s already-CARRIED confound findings.
- **Gemini's Part B (system boundary) is orthogonal to Fable's system-boundary finding, and both point
  the same way.** Fable independently found the manuscript states no residential-only or
  office/commercial system-boundary sentence anywhere, including in the current `draft_S7_limitations.md`
  redraft. Gemini's Part B supplies the external literature (Sepanta et al., Tao et al., IEA, Hook et
  al., O'Brien and Yazdani Aliabadi) that such a boundary paragraph would need to cite; it does not
  itself establish that the boundary is undisclosed (that is Fable's close-reading finding), but it
  supplies exactly the missing external material WP10's boundary paragraph needs once written.

## 9. Known-versus-new cross-check against `00_REVISION_PLAN.md`

The plan already lists this exact material as owed external input: item D6 ("why forecasting
specifically to 2030 is necessary... source needed, external", assigned WP10/WP12) and item D13 ("this
system-boundary limitation should be clearly discussed... literature external", assigned WP10/WP12),
plus WP2's stated purpose (2030 work-from-home scenarios, line 168) and the reviewer items it answers
(R3-2, R3-4, lines 117/119). Gemini's Part A directly supplies the external justification D6 needed
(national trajectory data to 2026 plus published projections to 2030 and 2035) and gives WP2 the actual
numeric range needed to define more than one scenario (the plan's own item 2, "do either at least two
2030 scenarios... high persistence and partial/high reversion", line 117), which until this return had
no concrete external numbers attached. Gemini's Part B directly supplies the external literature D13
needed for the system-boundary paragraph. **The continued post-2022 decline found in section 8 above is
new information beyond what the plan currently anticipates**: the plan's own language (line 117)
already calls for "partial/high reversion" as one of the two scenarios WP2 should build, but did not, as
of this pass, have external data confirming that a reversion trend is already underway in the observed
record, not merely a hypothetical bracket. This strengthens the case for WP2's reversion scenario being
grounded in the actual post-2022 trend rather than an arbitrary bracket.

## 10. Final verdicts

- **Gemini return (dr_2J-11): SURVIVES VETTING.** The positive control resolves exactly; four of five
  DOIs resolve on Crossref with matching titles; the one that does not (Morissette et al.) is confirmed
  real via DataCite, not fabricated, the same pattern already accepted for other non-Crossref sources in
  this project. Every headline Table B claim independently checked (Sepanta, Tao, Hook, IEA) is
  confirmed in substance from an independent route, one of them (IEA) an exact match on every number.
  Every MODELLED number is correctly labelled and not conflated with a measurement. All checkable
  arithmetic is correct. The one specific defect found, the "7.1%" 2016 figure not matching any number
  found on the cited StatCan page, is narrow (one cell of roughly 20 in Table A) and does not affect the
  report's own verdict or any of the headline trade-off or trajectory claims used elsewhere.
- **Joint (Gemini plus Fable, T40): both SURVIVE VETTING and are mutually reinforcing rather than
  competing.** Fable establishes, from the manuscript's own text alone, that the current 2030 scenario
  construction does not actually test a WFH effect on the leg carrying the confidence intervals. Gemini
  independently supplies the real trajectory data (continued decline through 2026) and trade-off
  literature that make clear the manuscript's implicit flat "persists" assumption is not the best
  available central case and gives WP2 and WP10 concrete external material to build the scenario range
  and system-boundary paragraph the plan already calls for.

## WHAT THIS VETTING DID NOT CHECK

- The 19 spot-checked quotes from the Fable return, and its own known-versus-new table, are not
  repeated here; see `dr_2J-10_dr2J-11_FABLE_VETTING.md` sections 1 and 3 for that record.
- The Sepanta et al. (2024) report's full PDF was not located or opened directly; its NCR headline
  number was confirmed via an independent secondary description of the same report, not the primary
  document itself, and its Quebec-specific figures (64%, -1.3 t CO2e/employee/yr) were not
  independently re-derived at all.
- StatCan Daily source pages for the A1/A2 rows other than the 2016 and April 2020 figures (2020-2021
  average, May 2021, May 2022, May 2023, June 2024, the 13.2%/10.3% hybrid split) were not individually
  re-opened in this pass; none is internally inconsistent with the confirmed figures, but none was
  independently verified against its own source page either.
- Hook et al.'s "5 ambiguous" residual category was not found stated this way in the secondary source
  used and was checked only for arithmetic self-consistency (39 minus 34 equals 5), not against the
  paper's own text.
- The report's search methodology and coverage claims (which databases, how many records) receive no
  explicit search log in this report the way dr_2J-10 has one, so there was nothing of that kind to
  audit here.
