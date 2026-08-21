# L26. Spain and Italy: which census tables actually deliver our four marginals, at our category boundaries?

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## 🔴 CORRECTIONS TO THE MASTER BRIEF — READ THESE BEFORE THE BRIEF ITSELF

1. **The corpus is HETUS only.** Canada and the United States are out of the paper.
2. **One survey wave per country, not several.**
3. 🔴 **The corpus is THREE countries: Spain 2009-10, United Kingdom 2014-15, Italy 2013-14.** France
   was excluded on 2026-08-15.
4. **There is no forecast and no temporal claim anywhere in the paper.**
5. **The fine-tuned model will never be released.**

---

## 🔴 READ THIS FIRST: TWO DECISIONS ARE ALREADY CLOSED AND THIS PROMPT IS NOT ASKING YOU TO REOPEN THEM

`RL24` answered the route question and the author ruled on the basis question on 2026-08-20. Both are
frozen. **Do not recommend an alternative to either.** Recommending one is a mandatory negative control
below.

| | ruled | why |
|---|---|---|
| **route** | **The national statistical offices.** INE, ONS via Nomis, ISTAT. | Eurostat merges homemaker with other-inactive (`CAS.L` category `2.4`) and drops the UK from the 2021 round. |
| **basis** | **The census round is the FROZEN PRIMARY.** The annual series (INE Padron plus EPA, ISTAT Bilancio plus RCFL, ONS MYE plus APS) is a **declared sensitivity**, reported separately and **never mixed** into the primary. | `prereg.md` section 5 requires one basis serving both the population synthesis and the null model. |

**We are not asking which source to use. We are asking for the table IDs and the numbers.**

---

## The question, in one sentence

**For Spain and for Italy, which specific 2011 census tables, reachable today at a URL you have opened,
publish national totals for age, sex, household composition and economic status, and what are the
category boundaries those tables actually use?**

## Why it is being asked

Our step document must produce `outputs_step5/marginals_<country>.csv`, one row per category, each row
carrying a source table ID, a cell code, a URL and a download date. That file is on the **critical path
of the paper headline claim**: the pre-registered null model rakes onto the held-out country published
marginals, so until the file exists the bar the model is measured against cannot be computed at all.

🔴 **The United Kingdom is already DONE and this prompt does not ask you to redo it.** It is reported
below in full because it is your calibration target. See Part D.

---

## Our four fields and their exact category values

These are frozen. They come from `tools/encoder.py` and cannot be changed to match a published table.

| field | values |
|---|---|
| `strat_age_band` | `11-14`, `15-24`, `25-34`, `35-44`, `45-54`, `55-64`, `65-74`, `75+` |
| `strat_sex` | `male`, `female` |
| `strat_hh_type` | `one_person`, `couple_no_children`, `couple_with_children`, `single_parent_with_children`, `other_complex`, `unknown` |
| `strat_econ_status` | `employed`, `unemployed`, `student`, `retired`, `homemaker`, `other_inactive`, `unknown` |

🔴 **The population of interest starts at age 11.** Our diary corpus has an age floor of 11, confirmed
by the author. Every marginal must therefore either be restricted to persons aged 11 and over, or be
reported with enough detail that we can restrict it ourselves.

---

# PART A — SPAIN, AND PART B — ITALY

Answer the following **separately for each country**. Where an item does not exist, write `NOT FOUND`
rather than substituting the nearest thing from the other country or from an annual series.

**A1 / B1. The tables.**
For each of the four fields, name the **census 2011 table**: its official table identifier, its title in
the original language, the exact URL you opened, and the date you opened it. 🔴 **A landing page that
returns HTTP 200 is not a table.** We were caught by exactly that this month. Say whether you retrieved
**numbers** or only a page that promises numbers.

**A2 / B2. The access route.**
For each table, state how a script can retrieve it without a browser: a REST or SDMX endpoint with the
full query string, a bulk file, or `NONE, manual download only`. If there is an API, give one complete
worked example URL and say what you got back when you called it.

* For Spain, we tried `https://servicios.ine.es/wstempus/js/ES/OPERACIONES_DISPONIBLES` on 2026-08-20.
  It returns HTTP 200 and a usable JSON list of operations, but **the 2011 Censos de Poblacion y
  Viviendas is not in that list**. Tell us where the 2011 census results actually live and how to query
  them.
* For Italy, `http://dati-censimentopopolazione.istat.it/SDMX/sdmx.ashx/GetDataStructure/ALL` returned
  **HTTP 302** on 2026-08-20, and `https://esploradati.istat.it` returns a 10 MB dataflow list in which
  **no dataflow name in English or Italian contains "census" or "censimento"**. Tell us whether the
  2011 census dataflows still exist, under what identifiers, and on which host.

**A3 / B3. The category boundaries, verbatim.**
For each table, list the published categories **as the table prints them**, in the original language,
with the code the table uses. Do not translate them into our categories. **We will do the mapping; you
supply the raw alphabet.** If age is published only in five-year bands, say so and give the bands.

**A4 / B4. The numbers.**
Give the national total and the count for each published category, for the tables you actually
retrieved. If you did not retrieve numbers, say so and give no numbers at all.

**A5 / B5. Licence and citation.**
Under what terms may these figures be reproduced in a paper, checked on what date, at what URL?

---

# PART C — THE FOUR PLACES WE ALREADY KNOW THE MAPPING IS AWKWARD

These are not hypothetical. Each was found in the UK data on 2026-08-20 and each will recur.

## C1. 🔴 The `11-14` band

Published five-year bands run `0-4, 5-9, 10-14, 15-19`. **No aggregate table isolates `11-14`.**

For the UK we solved this cleanly: **QS103UK, age by single year**, UK-wide, summed over ages 11 to 14.
It reproduces the published all-ages total to the unit.

**So the question for Spain and Italy is narrow: does a single-year-of-age census table exist, and at
what geography?** If yes, name it. If no, say so plainly, and name what would have to be subtracted
from what.

## C2. 🔴 Economic status is not published for the young or the old

`KS601UK` is titled **"All usual residents aged 16 to 74"**. It has a floor **and a ceiling**. So for
the UK, **two of our eight age bands have no economic-status marginal at all** and their values must be
assigned rather than fitted.

**What are the age limits of the Spanish and Italian census economic-status tables?** Give the exact
published wording. Do not assume they match the UK.

## C3. 🔴 The homemaker versus other-inactive split, which is the whole reason we are not using Eurostat

`KS601UK` separates **"Economically inactive: Looking after home or family"** from **"Long-term sick or
disabled"** and from **"Other"**. That separation is why the national-office route was chosen.

**Do the Spanish and Italian census tables make the same separation?** Quote the category labels. 🔴 **If
either country does not separate them, that is a finding we act on immediately** and it is far more
useful than a reassuring answer.

## C4. 🔴 A household category that does not map, and it is 8 percent of the UK

`KS105UK` publishes **"One family only: All aged 65 and over"** as a category of its own, outside the
married, cohabiting and lone-parent breakdown. It is **2,131,191 households, 8.06 percent of the UK
total**, and it is ambiguous between our `couple_no_children` and our `single_parent_with_children`.

**Do the Spanish and Italian household-composition tables carry an equivalent age-defined household
category?** If yes, name it and give its count. **And separately: is there any published table, in any
of the three countries, that splits such households by composition?**

## C5. The denominator, stated so you do not have to guess

Household composition is a count of **households**. Age, sex and economic status are counts of
**persons**. We know this and we are handling it. **Do not spend the report explaining it.** What we do
want: **does either country publish a person-level table of position in household, or household type of
the person**, which would let us express household type on a person base directly? Name it or write
`NOT FOUND`.

---

# PART D — 🔴 YOUR CALIBRATION TARGET: REPRODUCE THE UNITED KINGDOM

The UK marginals were assembled on **2026-08-20** from Nomis and are given here **in full**. Every
number below came from a CSV we downloaded and re-derived.

| field | source table | base | note |
|---|---|---|---|
| age | `QS103UK` (Nomis `NM_1531_1`) | 55,053,949 persons aged 11 and over | summed from single years; all-ages total 63,182,178 reproduced exactly |
| sex | `KS101UK` (Nomis `NM_158_1`) | 63,182,178 persons, **all ages** | 🔴 an approximation, see D1 |
| household type | `KS105UK` (Nomis `NM_1502_1`) | 26,442,096 households | 8.06 percent unallocated, see C4 |
| economic status | `KS601UK` (Nomis `NM_1511_1`) | 46,410,490 persons aged 16 to 74 | maps onto our six bands with residual **exactly 0** |

**Our UK age bands, persons aged 11 and over:**

| band | count | share |
|---|---|---|
| `11-14` | 2,971,665 | 5.398 % |
| `15-24` | 8,293,650 | 15.065 % |
| `25-34` | 8,431,789 | 15.316 % |
| `35-44` | 8,820,112 | 16.021 % |
| `45-54` | 8,737,554 | 15.871 % |
| `55-64` | 7,422,052 | 13.481 % |
| `65-74` | 5,480,225 | 9.954 % |
| `75+` | 4,896,902 | 8.895 % |

**Our UK economic-status mapping, which partitions the published base with zero residual:**

| our band | `KS601UK` cells summed | count |
|---|---|---|
| `employed` | In employment | 28,607,397 |
| `unemployed` | Economically active: Unemployed | 2,054,146 |
| `student` | active full-time student **plus** inactive student | 4,296,273 |
| `retired` | Economically inactive: Retired | 6,443,875 |
| `homemaker` | Looking after home or family | 1,981,470 |
| `other_inactive` | Long-term sick or disabled **plus** Other | 3,027,329 |
| | **sum** | **46,410,490**, equal to the published base |

**Two UK questions we could not answer ourselves, and you may be able to:**

**D1.** 🔴 **We found no UK-wide census table of sex by age.** `QS103UK` has no sex dimension;
`DC1117EW` and `LC1117EW` are England and Wales only. So our UK sex marginal is currently the
**all-ages** split, which is an approximation for an 11-plus population and is flagged as one in our
file. **Does a UK-wide sex-by-age 2011 census table exist on Nomis or elsewhere?** If it does not, say
so, and say whether assembling one from the separate national censuses (ONS for England and Wales, NRS
for Scotland, NISRA for Northern Ireland) is the only route.

**D2.** How does ONS itself classify **"One family only: All aged 65 and over"** in any other published
table? A cross-tabulation that splits it would settle C4 for the UK immediately.

🔴 **Your report is calibrated on Part D.** If you cannot reproduce a number we have already verified,
we will not trust your Spanish and Italian numbers either. **Report explicitly whether each UK figure
above matched what you found, and name any that did not.**

---

# PART E — THE QUESTION WE MAY NOT HAVE THOUGHT TO ASK

You have now seen the design: a synthetic population fitted by IPF onto national census marginals, each
person turned into a conditioning prefix, a diary generated for each by a model that never saw that
country, and the whole thing benchmarked against a null model raked onto **the same** marginals.

**Name the one thing most likely to be wrong with our marginals step specifically.** One specific
checkable thing, with the evidence that makes you suspect it and the cheapest test that would confirm
or kill it.

Four candidates we have already thought of, so do not offer any of them: the household versus person
denominator mismatch; the temporal gap between census rounds and diary waves; the missing
economic-status marginal at both ends of the age range; and suppressed cells at fine geographies.

---

## MANDATORY NEGATIVE CONTROLS FOR THIS REPORT

Answer all eight in plain sentences in Section G.

1. **List every URL you actually opened and retrieved data from**, separated from URLs you named but
   did not open. **Every number anywhere in your report must come from the first list.** A citation is
   not evidence until opened.

2. **For how many of the eight country-field combinations** (2 countries by 4 fields) **did you retrieve
   actual numbers, as opposed to identifying a table that should contain them?** Give the number. **If
   it is zero, say zero.** Zero is a useful answer and it tells us the route is manual download.

3. **Did you reproduce our UK figures in Part D?** Answer per figure. Name every one that did not
   match, with the value you found.

4. **Did you at any point recommend Eurostat, the Census Hub, or an annual series as the primary
   basis?** Both decisions are closed. Say plainly whether you did.

5. **Did you give any count, share or category boundary that you did not read in a retrieved table?**
   Say where. An engineering-plausible share is not a citation and our gate `G5.3` will reject it.

6. **Count the convenient findings.** The convenient answers here are: both countries publish
   single-year-of-age census tables; both separate homemaker from other-inactive; both have an open
   API; and neither has an age-capped economic-status table. 🔴 **If most of those came back convenient,
   stop and re-check.**

7. **Did you assume Spain and Italy publish the same table structure as the UK?** Say so explicitly per
   field. They are three separate national statistical systems and we expect them to differ.

8. **State the geography level of every table you report.** National totals are what we need. If a
   table exists only at municipal or provincial level and would have to be summed, say so, because
   summing suppressed cells is not the same as a published national total.

Also required, as in every round of this series:

* `NOT FOUND` beats an invented answer, always.
* Every table ID, quantity, licence or boundary carries **the date it was checked and the URL it came
  from**.
* 🔴 **Do not reproduce or reconstruct the contents of a paywalled or restricted table.** Say it is
  restricted and stop.
* Do not state, estimate or reproduce any result of our models, and do not comment on our hardware, our
  storage or our cluster. You cannot see them.
* No em dashes and no en dashes in the returned text.
