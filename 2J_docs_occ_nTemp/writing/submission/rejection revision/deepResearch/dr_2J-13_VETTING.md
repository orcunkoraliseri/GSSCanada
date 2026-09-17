# Vetting of dr_2J-13 (Gemini return: measured residential end-use split, calibration closure)

VERDICT: PARTIALLY SURVIVES. The CEUD numbers, the arithmetic, and most of the citations are
genuine and independently verified against live sources. But the return violates the prompt's own
scope guard by treating a modelled stock-accounting benchmark as if it satisfied a
"measured or survey-based" requirement, and it triggers the wrong pre-registered decision rule as a
result. A separate, serious basis question (does CEUD's all-fuel space heating total compare validly
to the paper's simulated per-m2 figure) is left completely unaddressed, and it is exactly the failure
mode the prompt was written to catch.

Vetted 2026-09-17. Method: WebFetch of the live NRCan CEUD tables (each with an explicit request for
the 2022 column, since the default view showed 2023), the StatCan RESD explanatory-notes PDF, and
Crossref DOI lookups for every peer-reviewed citation; independent recomputation of every PJ-to-kWh
conversion and every intensity and share with Python; a mechanical scan for em/en dashes and the word
"validat*". No em dashes or en dashes used in this document.

## 1. Scope compliance

The return does not answer the question asked. The prompt's scope guard is explicit: "A code-compliance
estimate or a modelled archetype value is not an answer." The return's own text states plainly that
direct physical sub-metering of the five end uses is NOT FOUND anywhere in Canada, and that the only
source it can offer, NRCan's Comprehensive Energy Use Database, "produces this disaggregation using the
Residential End-Use Model (REUM), which applies unit energy consumption (UEC) engineering stock
accounting to SHEU microdata and equipment shipment data, calibrated strictly to match Statistics
Canada's ... control totals." That is a description of a model, not a measurement or a survey. Despite
this, the return's own Summary Verdict says "USABLE under Canada's official national survey-calibrated
benchmark," which blurs a modelled stock-accounting product with the survey-based split the prompt
asked for. Section 3 of the SHEU-2019 findings (Location 1) is honest that SHEU itself carries no
end-use split. The CEUD numbers are real and correctly transcribed (see section 3 and 4 below), but
offering them as the answer, rather than as the closest available proxy under an explicit modelling
caveat, is a scope violation.

## 2. Pre-registered decision rule check (the single most important question)

The prompt has four rules. Rule 3 reads: "If the space heating figure specifically is NOT FOUND, the
breakdown is not run at all: the paper states that the measured end-use split was unavailable and
attributes the EUI gap to no single end use."

The return's own findings establish that the MEASURED space heating figure is NOT FOUND (direct
sub-metering: NOT FOUND; SHEU: NOT FOUND; utility/IESO studies: NOT FOUND; peer-reviewed literature:
NOT FOUND). The only space heating figure it supplies is CEUD's modelled stock-accounting estimate.
Read strictly against the prompt's own scope guard ("a modelled archetype value is not an answer"),
this means Rule 3 fires: the breakdown should not have been run, and the paper should state that the
measured split was unavailable, attributing the EUI gap to no single end use.

Instead, the return proceeds as though Rule 1 fired ("the split is found... unambiguous, the paper
reports the Table 5 EUI gap broken down by end use") and its section 6 explicitly assigns the entire
gap to space heating using the CEUD numbers.

What each option means for the paper:
- If Rule 3 is honored: the manuscript cannot say "the gap is in space heating." It states the
  measured/survey split was unavailable and leaves the EUI gap unattributed to any single end use.
  This is the more defensible position under the prompt as pre-registered.
- If the CEUD numbers are used anyway (the return's own path): every sentence built on them must
  carry an explicit, prominent modelled-benchmark caveat (which the return does supply in its section
  6, item 3), and the paper should not describe this as a "measured" or "survey" comparison anywhere,
  including headlines, abstract, or figure captions. This is a weaker but not indefensible position,
  provided the caveat is never dropped and the basis-comparability question in section 7 below is
  resolved first.
This document does not decide between the two; that is an editorial call for the paper's authors, not
this vetting pass.

## 3. Citation and identifier verification

**StatCan Table 25-10-0029-01.** The DOI `https://doi.org/10.25318/2510002901-eng` resolves (302
redirect) to `https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2510002901`, titled "Supply and
demand of primary and secondary energy in terajoules, annual." This matches the return's claim. The
table's own explanatory-notes publication (Statistics Canada catalogue 57-003-X, fetched and read in
full) confirms the table does contain sector rows including a dedicated "Residential" line within
"Energy use - final demand," so the return's claim that this table can report residential-sector
totals is structurally correct. The live interactive table would not surface its data cells to a
simple fetch (its numbers require picking parameters through JavaScript), so the exact 2022 cell value
of 1,380,174 TJ quoted by the return could not be independently re-pulled in this pass. Given the
table's known structure and the value's order of magnitude (about the same as CEUD's 1,454.1 PJ
residential total, not the much larger all-sector total), the value is plausibly the residential row,
but this is inference, not a confirmed cell read. VERIFIED (table identity, title, and structure);
CANNOT VERIFY (the specific 1,380,174 TJ cell value).

**StatCan Table 25-10-0060-01.** Confirmed to exist at `pid=2510006001`, "Household energy
consumption, Canada and provinces," 165 series, years 2011-2019, dimensioned by Geography, Energy type
(Total, Electricity, Natural gas, Heating oil), and Energy consumption (GJ, GJ per household,
proportion, number of households). This is an exact match to the return's description. VERIFIED.

**NRCan CEUD showTable.cfm URLs and table numbers (2, 35, 37, 39, 41).** All five fetched live for the
2022 column specifically (the un-parameterized fetch defaults to the newest year, 2023, which briefly
looked like a discrepancy until re-fetched asking explicitly for 2022). Every single PJ value in the
return's Table 1 (Ontario, all five dwelling types) and Table 2 (Canada) matches the live CEUD table
for 2022 exactly: Ontario All Residential (rn=2) 331.4/92.7/54.6/17.2/19.3/515.2 PJ; Single Detached
(rn=35) 238.0/56.2/32.4/11.5/14.9/353.1 PJ; Single Attached (rn=37) 45.6/14.9/9.0/2.5/2.7/74.8 PJ;
Apartments (rn=39) 46.0/21.3/12.9/3.2/1.7/85.2 PJ; Mobile Homes (rn=41) 1.8/0.2/0.1/0.04/0.05/2.2 PJ;
Canada (rn=2, juris=ca) 905.2/265.2/189.5/57.7/36.5/1454.1 PJ. Floor space and household activity bases
(Ontario 901.8 million m2 / 5,808.5 thousand households; Canada 2,305.0 million m2 / 15,416,000
households) also match live CEUD "Activity Variables" exactly. VERIFIED, table numbers and archetypes
correctly matched.

**SHEU-2019.** The page `https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm`
resolves and is titled "2019 Survey of Household Energy Use (SHEU-2019) Data Tables," confirming the
survey's existence, year, and that it publishes energy-intensity tables in the 3.x series (per household
and per heated area) without an end-use breakdown, exactly as the return states. One nuance: the fetched
page describes 3.2a/3.3a as "by region" and 3.2b/3.3b as "by dwelling type" at the Canada level, while
the return's Table 3 cites "Table 3.2a, 3.3a" for Ontario dwelling-type rows and "Table 3.2b, 3.3b" for
Canada dwelling-type rows, i.e. the opposite lettering convention from what a single fetch surfaced.
This may simply reflect a separate lettering scheme per geography tab that a single page fetch cannot
resolve. VERIFIED (survey identity, year, absence of end-use split); table-letter assignment CANNOT
VERIFY at this resolution, not FABRICATED.

**Peer-reviewed citations, one by one:**
- Abdeen, Kharvari, O'Brien, Gunay (2021), "The impact of the COVID-19 on households' hourly
  electricity consumption in Canada," Energy and Buildings, vol. 250, article 111280. Crossref-confirmed
  exactly (title, journal, volume, year, all four authors). Independent web search confirms 500 Ottawa
  households and utility billing/interval data, matching the return's description. VERIFIED.
- Rouleau and Gosselin (2021), cited by the return as "Applied Energy 290, 116565." Crossref confirms
  the DOI resolves to "Impacts of the COVID-19 lockdown on energy consumption in a Canadian social
  housing building," Applied Energy, year 2021, correct authors and article number 116565, but the
  volume is 287, not 290. WRONG DETAIL (volume number). The described study content (40-unit social
  housing building, Cite Verte eco-district, Quebec City) matches independently found sources. The
  specific claim that it "sub-metered lighting and plug loads" while heating ran on "a shared hydronic
  loop without individual unit space heating measurements" could not be confirmed from the abstract
  alone (full text paywalled). CANNOT VERIFY that specific technical detail.
- Makonin, AMPds/AMPds2. Confirmed: a single detached home in Burnaby, BC, monitored 2012-2014 (originally
  published as "Electricity, water, and natural gas consumption of a residential house in Canada from
  2012 to 2014," Scientific Data), with genuine circuit-level sub-metering. VERIFIED.
- Makonin, HUE dataset, cited by the return as "Makonin 2018" covering "28 homes." Independent sources
  (Harvard Dataverse, Data in Brief) show the dataset's own documentation states 22 houses, not 28, and
  the formal peer-reviewed publication is dated 2019 (Data in Brief, vol. 23, article 103744), not 2018,
  though the dataset was informally released in 2018. WRONG DETAIL (home count: 22 vs stated 28; and the
  return's year (2018) is the informal release date, not the citable publication year).
- Fung, Aydinalp, Ugursal, Farahbakhsh, Canadian Residential Energy End-use Model (CREEM). Confirmed as
  a real, correctly attributed bottom-up stock model based on 1993 SHEU data. VERIFIED.
- Swan et al., Canadian Single-Detached and Double/Row Housing Database (CSDDRD). Confirmed real,
  approximately 17,000 EnerGuide-audited houses, used with ESP-r/CHREM for stock simulation, matching
  the return's characterization exactly. VERIFIED.
- Papineau et al., cited by the return as "Papineau et al. 2022." The only matching paper found,
  "Conditional demand analysis as a tool to evaluate energy policy options on the path to grid
  decarbonization" (Papineau, Yassin, Newsham, Brice), was published in Renewable and Sustainable Energy
  Reviews, vol. 149, in 2021, not 2022, and matches the return's description (CDA applied to Canadian
  billing data to isolate heat pump technology impacts) closely. WRONG DETAIL (year: 2021, not 2022). No
  separate 2022 Papineau CDA/heat-pump paper was found.
- Cadmus / IESO 2018 Residential End-Use Survey. Confirmed: final report dated November 28, 2018,
  hosted at ieso.ca, 3,159 households surveyed (return says "over 3,000"), stratified by building type
  and region, exactly as described. VERIFIED.

## 4. Internal arithmetic check

Recomputed every conversion in Python (1 PJ = 277,777,777.8 kWh) for both Ontario tables (all five
dwelling types) and the Canada table.
- Every stated "Converted Energy (Million kWh)," floor-area intensity (kWh/m2/yr), and household
  intensity (kWh/hh/yr) in Table 1 and Table 2 reproduces to within rounding (typically under 0.05,
  the size expected from the source PJ figures being published to 1-3 significant digits). No
  arithmetic error found in any of the 30 converted cells checked.
- Each archetype's five end uses sum to its own stated total to within 0.1 PJ (e.g. Single Detached
  238.0+56.2+32.4+11.5+14.9 = 353.0 vs stated 353.1; Apartments sums to 85.1 vs stated 85.2), consistent
  with normal rounding in a source published to one decimal place, not an error.
- The five archetype totals (353.1+74.8+85.2+2.2 = 515.3) sum to within 0.1 PJ of the stated Ontario
  All Residential total of 515.2 PJ. Same rounding-scale agreement.
- Per end use, the four archetypes sum to the All Residential row to within 0.1-0.2 PJ in every case
  (space heating sums exactly: 238.0+45.6+46.0+1.8 = 331.4 = stated). No real mismatch.
- Ontario household counts across the four archetypes sum to 5,808,400 against a stated total of
  5,808,500 (100-household rounding gap); floor areas sum exactly to 901.8 million m2. No issue.
- Percentage shares in both Table 1 (All Residential) and Table 2 (Canada) reproduce the published PJ
  ratios to within 0.05 percentage points and sum to 99.9-100.0%. No issue.
- SHEU-2019 Table 3 GJ-to-kWh conversions (1 GJ = 277.778 kWh) all reproduce to within 0.04 kWh, no
  issue.
Conclusion: the arithmetic in this return is clean. No PJ-to-kWh, intensity, or share conversion is
wrong. This is a real strength of the return.

## 5. Consistency contradiction hunt

**Chat-side summary vs. saved file (Ontario Single Detached water heating).** The task brief records
the author's chat-side summary of this same run as reporting 68.7 PJ / 32.81 kWh/m2, floor area 221.7
m2/dwelling, stock 3,197,358, while the saved file's Table 1 reports 56.2 PJ / 26.86 kWh/m2 with
581.3 million m2 total floor area and 5,808,500 (Ontario total) / 3,202,500 (Single Detached)
households. These are two different PJ figures for what is claimed to be the same quantity. Working
the numbers: the saved file is fully self-consistent (56.2 PJ over the file's own 581.3 million m2
gives 26.86 kWh/m2 exactly, matching the file). The chat-side figures are also self-consistent with
each other (68.7 PJ over 581.3 million m2, the FILE's floor area, gives 32.81 kWh/m2, matching the
chat-side intensity almost exactly), but NOT with the chat-side's own claimed floor area: 221.7
m2/dwelling times 3,197,358 dwellings implies 708.8 million m2, which if paired with the chat-side's
own 68.7 PJ figure gives 26.92 kWh/m2, i.e. very close to the FILE's water heating intensity (26.86),
not the chat-side's own stated 32.81. In short: the chat-side output appears to have paired the wrong
PJ figure (68.7, source unclear, not matching any value in the saved file) with the saved file's own
floor area (581.3 million m2), while separately quoting a floor-area-per-dwelling and dwelling-stock
pair that reconcile with neither the saved file nor its own PJ number. This is a real, first-principles
confirmed internal inconsistency across two outputs of "the same run": at least three of the four
numbers involved (PJ, floor area, or stock) cannot all be correct simultaneously. The saved file's
Table 1 is the one that is internally self-consistent and matches the live CEUD source (see section 3);
the chat-side summary is not reconcilable with either the file or a plausible independent floor-area
basis. **The saved file is the version that should be trusted; the chat-side summary should not be used
for anything.**

**Positive control vs. Table 2 Canada residential total.** The positive control reports Canada's 2022
residential-sector energy demand (StatCan RESD, table 25-10-0029-01) as 1,380,174 TJ = 1,380.174 PJ.
Table 2 (NRCan CEUD, calibrated to the same StatCan RESD control totals per the return's own text)
reports the Canada 2022 residential total as 1,454.1 PJ. These are two numbers for what should be the
same or a closely related quantity (Canada, residential sector, 2022, secondary energy), differing by
73.9 PJ, or 5.1%. This is a real, non-trivial discrepancy between the return's own "positive control"
(used to certify that its search worked) and the headline CEUD total used throughout the rest of the
return. It does not look large enough to indicate the positive control pulled the wrong quantity
entirely (an all-sector, all-industry total for Canada would be many times 1,380 PJ), but a 5% gap
between two supposedly control-totaled numbers is the kind of cross-source disagreement the return
should have flagged and did not.

## 6. Prompt constraint compliance

Mechanical scan of the full 27,117-byte results file for U+2014 (em dash), U+2013 (en dash), and
case-insensitive "validat" (to catch "validate," "validates," "validation," etc.): zero occurrences of
all three. PASS, no violations found anywhere in the file.

## 7. Load-bearing claim audit (the failure mode the prompt was written to catch)

The return's headline conclusion (section 6) is that the manuscript's simulated space heating
(12.6-29.5 kWh/m2/yr) sits 4 to 9 times below the CEUD Ontario benchmark (71.3-113.7 kWh/m2/yr for
apartments through single detached), and that "the calibration gap is unequivocally located in the
thermal space heating load."

This comparison is only valid if both the floor-area denominator and the fuel scope of the numerator
match. The return never checks either:
- **Floor-area basis.** CEUD's activity variable is explicitly labelled "heated floor space" (confirmed
  live at the CEUD Ontario table). Whether the manuscript's own EnergyPlus per-m2 basis (gross floor
  area, conditioned floor area, or heated floor area only) is the same definition is not addressed
  anywhere in the return, because the return has no visibility into the manuscript's own model
  definitions; it only had the prompt's stated 12.6-29.5 kWh/m2/yr range to work from. This basis
  equivalence is asserted by neither the prompt nor the return, only assumed.
- **Fuel scope.** CEUD's space heating figure is secondary energy consumption summed across ALL fuels
  used for space heating in the Ontario housing stock (electricity, natural gas, heating oil, wood),
  as the return's own methodology paragraph states. In Ontario, most of that stock is gas-heated. If the
  manuscript's simulated archetypes model an electric heating system (or a heat pump with a
  coefficient of performance above 1), the two numbers are not comparable on a like-for-like fuel or
  efficiency basis: CEUD counts the raw fuel energy burned by furnaces at typical combustion
  efficiencies well under 100%, not the useful heat delivered, while a simulated electric system's site
  energy could differ from a useful-heat-equivalent gas figure by a large factor having nothing to do
  with the building's thermal performance. The return does not name or rule out this possibility
  anywhere in its text.
Because neither the floor-area-definition match nor the fuel-scope match is confirmed, the "4 to 9
times" figure could be genuinely diagnostic of an undersized simulated heating load, or it could be
substantially an artifact of comparing different denominators and different fuel/efficiency scopes.
The return supplies the correct raw numbers (see section 3-4) but does not supply the missing basis
check the prompt explicitly asked the researcher to protect against ("a mismatched denominator... would
produce a fake agreement or a fake gap. Any unit conversion you perform must be shown as a step, not
silent, and the floor-area basis must be named in the source or the comparison is invalid"). Naming
the floor-area basis (which it does) is not the same as confirming it matches the paper's own basis
(which it does not do, and could not do without also being handed the manuscript's HVAC and floor-area
definitions). This is the single largest unresolved risk in the return.

## Citation table

| Claim | Identifier | Verdict | Evidence |
|---|---|---|---|
| StatCan positive control table | 25-10-0029-01 / DOI 10.25318/2510002901-eng | VERIFIED (identity/title); CANNOT VERIFY (2022 cell value) | Redirects to real StatCan table page; RESD explanatory PDF confirms residential-sector row exists |
| StatCan household energy table | 25-10-0060-01 | VERIFIED | Confirmed at pid=2510006001, matches dimensions/years described |
| NRCan CEUD Ontario All Residential | Table 2, rn=2, juris=on, year=2023 (2022 column) | VERIFIED | Live-fetched 2022 column matches return exactly |
| NRCan CEUD Ontario Single Detached | Table 35, rn=35 | VERIFIED | Live-fetched 2022 column matches return exactly |
| NRCan CEUD Ontario Single Attached | Table 37, rn=37 | VERIFIED | Live-fetched 2022 column matches return exactly |
| NRCan CEUD Ontario Apartments | Table 39, rn=39 | VERIFIED | Live-fetched 2022 column matches return exactly |
| NRCan CEUD Ontario Mobile Homes | Table 41, rn=41 | VERIFIED | Live-fetched 2022 column matches return exactly |
| NRCan CEUD Canada | Table 2, juris=ca | VERIFIED | Live-fetched 2022 column matches return exactly |
| SHEU-2019 survey and tables | oee.nrcan.gc.ca .../sheu/2019/tables.cfm | VERIFIED (existence/scope); CANNOT VERIFY (exact table-letter assignment per geography) | Page confirms survey, year, 3.x table series, no end-use split |
| Abdeen et al. 2021 | DOI 10.1016/j.enbuild.2021.111280 | VERIFIED | Crossref exact match; 500-Ottawa-household description independently confirmed |
| Rouleau and Gosselin 2021 | DOI 10.1016/j.apenergy.2021.116565, cited as "vol. 290" | WRONG DETAIL (volume is 287, not 290) | Crossref confirms title/authors/year/article number; volume mismatch |
| Makonin AMPds/AMPds2 | ampds.org / Scientific Data | VERIFIED | Single Burnaby, BC home, 2012-2014, confirmed independently |
| Makonin HUE, cited as "2018," "28 homes" | DOI 10.1016/j.dib.2019.103744 | WRONG DETAIL (22 homes, not 28; formal publication is 2019) | Harvard Dataverse / Data in Brief confirm 22 houses and 2019 publication |
| Fung et al., CREEM | no DOI cited | VERIFIED | Independently confirmed model, authors, 1993 SHEU basis |
| Swan et al., CSDDRD | no DOI cited | VERIFIED | Independently confirmed, ~17,000 houses, ESP-r/CHREM |
| Papineau et al., cited as "2022" | matches Renewable and Sustainable Energy Reviews vol. 149 (2021) | WRONG DETAIL (year is 2021, not 2022) | Only matching CDA/heat-pump/Canada paper found is dated 2021 |
| Cadmus/IESO 2018 REUS | ieso.ca REUS final report | VERIFIED | Final report Nov 28 2018, 3,159 households, matches description |

## Findings, ranked by threat to a paper number

1. **Rule 3 should fire, not Rule 1, and the return's own Verdict does not say so.** Because no
   measured or survey-based space heating figure exists (the return's own search confirms this), the
   prompt's pre-registered logic says the end-use breakdown should not be run at all. The return runs
   it anyway using a modelled benchmark and states in its own section 6 that the gap is "unequivocally
   located" in space heating. If the manuscript repeats that sentence, it is making a claim the
   pre-registered decision rule was specifically designed to prevent. This threatens any paper sentence
   that assigns the EUI gap to a specific end use.
2. **The floor-area-basis and fuel-scope equivalence behind the "4 to 9 times" claim is unconfirmed.**
   CEUD's space heating total spans all fuels at raw combustion energy, not useful heat; the paper's
   simulated figure's fuel type and floor-area definition are not checked against this in the return.
   If they differ, the "4 to 9 times" figure is not a clean measure of anything about the building
   model's fidelity. This threatens the specific magnitude (4x-9x) that the paper would headline.
3. **Chat-side vs. saved-file contradiction for Ontario Single Detached water heating (68.7 PJ / 32.81
   kWh/m2 vs 56.2 PJ / 26.86 kWh/m2).** The saved file is internally consistent and matches the live
   CEUD source; the chat-side numbers do not reconcile with themselves or the file. Any number quoted
   from the chat conversation rather than the saved file table would be wrong. Threatens any number the
   author might have already written down from memory of the chat session rather than from this file.
4. **Positive control (1,380.174 PJ) disagrees with the CEUD Canada residential total (1,454.1 PJ) used
   for the headline gap, by 5.1%.** Both cannot be treated as exact for the same quantity. Does not
   break the space-heating-specific numbers (which come only from CEUD), but undermines an unqualified
   claim that the search's own quality-control step "succeeded completely."
5. **Three peer-reviewed citations carry a wrong detail** (Rouleau and Gosselin volume 287 vs stated
   290; Papineau et al. year 2021 vs stated 2022; HUE dataset 22 homes vs stated 28, and 2019
   publication vs stated 2018). None of these citations carry numeric values used in the paper's
   calibration argument; they are background literature-review citations. Low threat to any specific
   paper number, but each should be corrected before citing.
6. **SHEU-2019 table-letter assignment (3.2a/3.3a vs 3.2b/3.3b) could not be confirmed at this
   resolution.** These SHEU whole-house intensities are not used in the return's own headline argument
   (which relies on CEUD, not SHEU), so this has essentially no bearing on any paper number, but the
   citation format should be checked before quoting a specific table letter.

## What I could not verify and why

- The exact 2022 data-cell value for the StatCan positive control (1,380,174 TJ) could not be
  independently pulled from the live interactive StatCan table, because its data is rendered through a
  JavaScript-driven customization tool that a simple page fetch cannot query; only the table's identity,
  title, and structural existence of a residential-sector row could be confirmed.
- The specific technical claim that Rouleau and Gosselin (2021) sub-metered lighting and plug loads
  separately from a shared hydronic heating loop could not be checked against the paper's full text,
  which sits behind a paywall; only the bibliographic facts (authors, journal, year, topic, building
  size and location) were confirmed.
- Whether the SHEU-2019 table lettering the return cites (3.2a/3.3a for dwelling-type rows at the
  Ontario level) matches NRCan's actual per-geography table-naming convention could not be resolved
  from a single page fetch, which surfaced only the Canada-level convention (3.2a/3.3a = by region,
  3.2b/3.3b = by dwelling type).
- Whether the manuscript's own simulated space heating basis (floor-area definition and heating fuel
  or system type) matches CEUD's "heated floor space" and all-fuel secondary-energy definitions is
  outside what this vetting pass or the deep-research return itself could check; it requires the
  manuscript's own model documentation, which was not part of either the prompt or the return.
