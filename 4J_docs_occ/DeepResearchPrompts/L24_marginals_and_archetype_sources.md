# L24. Which published sources can we actually reach, open and use, for census marginals and for building archetype parameters?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

The master brief predates twenty-three reports and a long series of author decisions. **Five things in
it are now wrong, and the third one governs this entire round.**

1. **The corpus is HETUS only.** Canada and the United States are out of the paper.
2. **One survey wave per country, not several.**
3. 🔴 **The corpus is THREE countries, not four. France was excluded on 2026-08-15.** The three, with
   the exact waves we hold, are:
   * **Spain, 2009-10** (`eet_2009_2010`)
   * **United Kingdom, 2014-15** (`uktus_2014_2015`)
   * **Italy, 2013-14** (`usodeltempo_2013_2014`, ISTAT)
4. **There is no forecast and no temporal claim anywhere in the paper.**
5. **The fine-tuned model will never be released.** The evaluation is leave-one-country-out transfer.

---

## The question, in one sentence

**For Spain, the United Kingdom and Italy, which published sources actually deliver (a) population
marginals for age, sex, household type and economic status, and (b) residential building envelope and
system parameters, in a form we can open, cite by table ID, and re-download later, and under what
licence?**

This round is about **reachability and fitness for our specific strata**, not about method. We are not
asking how to do iterative proportional fitting, and we are not asking whether TABULA is a good
typology. We are asking **what actually exists, what opens, and what it contains**.

## Why it is being asked, so you can tell a useful answer from a complete one

Two work items in our pipeline are blocked on this, and one of them turns out to sit on the critical
path of the paper's headline claim.

**(a) The marginals.** We synthesise a population per country by IPF onto published census marginals,
then condition the generator on each synthetic person. Separately, our **pre-registered null** is a
pool of real diaries from the other two countries, raked onto **the held-out country's published
marginals**. The pre-registration says, in the frozen text: *"the same marginals the model was given,
the same geography, the same strata. A null built on different marginals from the model's is not a
null, it is a handicap."* So the same tables serve both, and until they exist the headline gate cannot
be computed at all.

🔴 **The contamination rule that makes this delicate.** For the **held-out** country, every marginal
must trace to a **published** table. Any quantity derived from that country's own survey microdata is
contamination, it would make our transfer result look **better**, and it would leave no trace in the
result. So we need the table ID, the URL, the date, and the licence, for each marginal.

**(b) The archetypes.** There is no official library of European residential EnergyPlus models. We
intend to build archetype IDFs from TABULA / EPISCOPE parameters. Our step document records that
TABULA distributes "parameter tables, Excel workbooks and national typology brochures, not
simulation-ready models". We need to know exactly which of those are **machine-readable and
downloadable**, per country, and what a row of them contains.

---

# PART A — THE MARGINALS

## A1. Our strata, exactly. Answer against these, not against generic census categories.

The generator is conditioned on six fields. Four of them are demographic and need marginals:

| field | our categories, verbatim |
|---|---|
| `strat_age_band` | `11-14`, `15-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65-74`, `75+` |
| `strat_sex` | `female`, `male` |
| `strat_hh_type` | `one_person`, `couple_no_children`, `couple_with_children`, `single_parent_with_children`, `other_complex`, `unknown` |
| `strat_econ_status` | `employed`, `unemployed`, `student`, `retired`, `homemaker`, `other_inactive`, `unknown` |

🔴 **Two of these are known to be awkward and we want the awkwardness reported, not smoothed over.**

* **The age floor is 11.** Our corpus admits respondents from age 11 up, by author decision. Most
  census tabulations start at 0, or use 15+ or 16+ for economic status. **Report the actual lowest
  band each source publishes.** Do not tell us a table "can be aggregated to match" unless you have
  opened it and seen the bands.
* **`homemaker` and `other_inactive` are separate in our data.** Many labour-force tabulations collapse
  everything that is not employed or unemployed into a single "inactive". **Say which sources keep
  them apart and which do not.**

## A2. The three candidate routes. Evaluate each, per country.

**Route 1. Eurostat census database, national level.**
**Route 2. Eurostat census database, NUTS-2 regional level.**
**Route 3. The national statistical offices: INE (Spain), ONS and NISRA and NRS (United Kingdom),
ISTAT (Italy).**

For each route and each country, report:

* the **exact table or dataset identifier**, not a portal name;
* whether it is reachable **without a login**, and by what mechanism: JSON-stat API, SDMX, bulk file,
  or manual click-through only;
* the **census round or reference year** it covers, and whether that year is anywhere near our diary
  waves (2009-10, 2013-14, 2014-15);
* which of our four fields it actually cross-tabulates, and at what depth. A table giving age and sex
  separately is not the same as one giving age by sex;
* the **licence**, quoted, with the date you checked it;
* whether cells are **suppressed, rounded or flagged**, and how that is signalled in the payload.

## A3. 🔴 The United Kingdom question, which we expect to be the hard one

The United Kingdom left the European Union in 2020. **Does the United Kingdom appear in Eurostat's
census tables at all, and for which census rounds?** If the 2011 round includes it and the 2021 round
does not, say exactly that. If Eurostat carries no United Kingdom census data at any round, say that
plainly, because it would eliminate Route 1 for one of our three countries and force a mixed-source
design that our contamination argument then has to defend.

Related and equally concrete: the United Kingdom's 2021 census was **not** a single exercise. England
and Wales, Scotland and Northern Ireland ran separately, and Scotland ran a year late. **Report
whether a single UK-wide table exists for each of our four fields, or whether it must be assembled
from three sources.** If it must be assembled, that is a finding and we will act on it.

## A4. The temporal mismatch, stated so it cannot be answered vaguely

Our diaries are from 2009-10, 2013-14 and 2014-15. Census rounds are 2011 and 2021. **There is no
census year that matches any of our waves.**

We are not asking you to solve this. We are asking you to report, per country and per source, **what
intercensal or annual alternatives exist** that cover our actual diary years: labour force surveys,
population and housing statistics, annual demographic balances, household composition series. For
each, the same reachability and licence detail as A2.

🔴 **Do not recommend interpolating between census rounds.** If interpolation is the only route, say
so and stop there; the decision to interpolate is ours and it changes the contamination argument.

---

# PART B — THE ARCHETYPE PARAMETERS

## B1. What TABULA and EPISCOPE actually distribute, per country

We have confirmed that `webtool.building-typology.eu` and `episcope.eu` return HTTP 200. That is not
the same as knowing what can be downloaded.

For **Spain, the United Kingdom and Italy**, report:

* whether a **downloadable data file** exists (Excel, CSV, XML, anything machine-readable) as opposed
  to a PDF brochure, and its URL;
* whether the web tool has a **documented export or data endpoint**, or whether the data is only
  reachable by driving its interface. 🔴 **If the only route is scraping an undocumented back-end, say
  so.** We will not put numbers of unverifiable provenance into a provenance file;
* the **licence and any terms of use**, quoted, with the date checked. State explicitly whether
  redistribution of derived parameter tables is permitted;
* which **construction period bands** each national typology uses, verbatim. These become an axis of
  our simulation campaign and we cannot invent them;
* what a single archetype row actually contains: U-values by element, geometry, air change rate,
  system efficiencies, and whether values are given as **as-built** or **post-refurbishment** variants.

## B2. What TABULA does not give, which our own document says we must record

Our step document requires us to write down what TABULA does not supply and what we assumed instead,
because *"an assumed value that is not written down becomes a fact the moment someone reads the code"*.

**So: name the parameters an EnergyPlus residential model needs that the TABULA tables do not carry.**
Infiltration schedules, internal gain assumptions, setpoints, ventilation control, window operation,
thermal mass distribution, whatever it is. For each, say whether any companion EPISCOPE deliverable
supplies it, or whether it must come from somewhere else.

## B3. The alternative routes, briefly

Only if they are real and reachable: TEASER, CityGML or CityJSON building stock datasets with
attributes, national building stock observatories, the EU Building Stock Observatory, or any published
set of European residential EnergyPlus or IDF models. **For each, the same reachability and licence
detail.** If none of these delivers simulation-ready residential models for our three countries, say
so in one sentence; that is limitation F2 in our paper and a clean negative is useful.

## B4. The baseline schedule we benchmark against

Our foil is **ISO 13790 Annex G Table G.12** and **Italy's UNI/TS 11300-1**, both specifying a flat
continuous 4.0 W/m2 internal gain. A previous round could not open EN 16798-1 and correctly refused to
reconstruct it.

**Confirm or refute, from the standards themselves or from an open secondary source that quotes them
with a page reference:** that those two documents specify a flat continuous residential internal gain,
and what the value and its basis of area are. 🔴 **If you cannot open the standard, say you cannot open
the standard.** Do not reconstruct a table. The previous refusal was the correct behaviour and is worth
more to us than a plausible number.

---

# PART C — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: a language model fine-tuned on time-use diaries from three European
countries, evaluated by holding one country out entirely, driving synthetic populations built by IPF
onto published census marginals, feeding EnergyPlus archetypes built from TABULA parameters.

**Name the one thing most likely to go wrong in the marginals-to-population-to-conditioning path
specifically.** Not a generic risk. One specific checkable thing, with the evidence that makes you
suspect it and the cheapest test that would confirm or kill it.

Three candidates we have already thought of, so do not offer any of them as your answer: that census
categories will not align with our strata; that no census year matches our diary years; and that a
marginal can be published and still have been computed by the statistical office from the same
microdata we hold out.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all six in plain sentences in Section G.

1. **List every URL you actually opened**, separated from URLs you name but did not open. **A URL is
   not evidence until opened.** For every table identifier you give in Part A or Part B, state whether
   you opened the table itself or only its landing page. We have been burned by this: a landing page
   returning HTTP 200 tells you nothing about whether the data behind it exists.

2. **How many of our four strata fields can be obtained, cross-tabulated, from a single reachable
   table, per country?** Give the number per country. **If it is zero for any country, say zero.**

3. **Does the United Kingdom appear in Eurostat census data, yes or no, and for which rounds?** A
   direct answer, not a description of the portal.

4. **Report the actual lowest published age band for each source you recommend.** If it is not
   compatible with our floor of 11, say so explicitly rather than saying it "can be adapted".

5. **Count the convenient findings.** The convenient answers here are: one API serves all three
   countries, the categories align with ours, the licences permit everything, and TABULA has a clean
   machine-readable export. 🔴 **If most of those came back convenient, stop and re-check.** Three
   separate national statistical systems, one of them outside the EU, aligning cleanly with a set of
   strata derived from a different survey family would be surprising.

6. **Verify every DOI through CrossRef and report the title the API returned.** State explicitly
   whether any DOI resolved to a different paper than the one you cited. This series has been caught
   three times by a real author from the right field attached to the wrong document.

Also required, as in every round of this series:

* `NOT FOUND` beats an invented answer, always. A missing table reported as missing is a result.
* Every version, threshold, quantity, licence or category list carries **the date it was checked and
  the document it came from**.
* 🔴 **Do not reproduce, estimate or reconstruct the contents of a paywalled table or standard.** Say
  it is paywalled and stop.
* Do not state, estimate or reproduce any result of our models, and do not comment on our hardware,
  our storage or our cluster. You cannot see them.
* Do not recommend a source on grounds of convenience, tidiness or familiarity. Recommend the one the
  evidence supports, or report that the evidence does not support one.
* No em dashes and no en dashes in the returned text.
