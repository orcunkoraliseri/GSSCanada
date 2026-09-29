# T44. Which datasets let us train an occupancy model and score it without people

Paste `00_MASTER_BRIEF.md` first (read its sections 9 and 11), then `_RESPONSE_TEMPLATE.md`, then this
prompt, in one fresh session. **Run it alone: do not run any other prompt in this session, before or
after.** Written 2026-09-28. Your files are `RT44_open_data_with_automatic_truth.md` and
`RT44_pages.log`. It does not depend on `T43`; the two may run in either order.

## Why we are asking

Every candidate form for the fifth paper (brief section 11; `B1` to `B7` are defined in `T43`, and
repeated in one line each below) needs two things in the same dataset: enough records to train a model
on one GPU node, and a truth the model can be scored against with no person labelling or rating
anything. We need to know which datasets actually hold both, on terms a Canadian university can meet.

* `B1` diaries linked to measured household electricity; `B2` smart-meter data joined to a household
  survey; `B3` open time-use corpora; `B4` paired EnergyPlus runs (we generate these ourselves, so
  list only public simulation sets that could serve as a second test); `B5` repeated survey cycles;
  `B6` meter or smart-home data with measured presence; `B7` time-use surveys as the reference for
  language-model households.

## What we need

### Item 1. The dataset cards

One Section F row per dataset, using the data-source card of brief section 9, plus three columns:
**forms served** (`B1` to `B7`); **the truth variable**, quoted from the documentation (for example
"occupancy ground truth from PIR sensors", "half-hourly metered consumption"), and whether it was
measured, reported by the household, or simulated; **can it be scored without people** (yes, or no
with the reason).

### Item 2. What is missing

For each form, say whether at least one dataset serves it on open or registration terms, only on
application, or not at all. Say plainly which forms have no usable dataset. **Time limit:** our GPU
access ends in about four weeks (brief section 11), so for every dataset quote any stated turnaround
for access; an application with no stated turnaround under one week counts as not usable in time.

## Named leads (candidates to check, not facts; some may be closed, moved or never have existed)

UK Data Service (METER household electricity and time-use study; UK Time Use Survey 2014-15; Smart
Energy Research Lab, SERL); Edinburgh DataShare (IDEAL household energy dataset); Irish Social Science
Data Archive (CER smart metering trial with household survey); Harvard Dataverse (HUE, hourly energy
use of homes in British Columbia); Pecan Street Dataport (academic licence); REFIT and UK-DALE; the ECO
dataset (ETH Zurich, with occupancy ground truth); Low Carbon London; NEEA Residential Building Stock
Assessment; NREL End-Use Load Profiles and ResStock; US BLS ATUS; IPUMS MTUS and ATUS-X; Statistics
Canada GSS public files through ODESI or Borealis; Canadian utility open data. The ecobee Donate Your
Data programme was found in an earlier round to have research terms that could not be read on any
public page; report its current state only if a logged page shows it.

## Hard constraints specific to this prompt

* A dataset is `reachable` only if its landing or download page returned 200 and is logged on the date
  checked. Described in a paper but not reached is `COULD NOT OPEN` in Section G.
* The truth variable and the access terms count only if quoted from a logged page. "Free for
  researchers" is `application` unless the licence text says open.
* Say for every dataset whether it covers Canada. A dataset outside Canada is still admitted; say so.
* One verified example of use in building energy research per dataset, with its CrossRef title, or
  `NONE FOUND`.
* Do not name any person connected to the researcher's funding proposals or host laboratory.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first, in at most eight sentences: which forms have a usable dataset with
automatic truth, which do not, and which single dataset serves the most forms. **Section F** is
item 1. **Section D** is item 2, one row per form, marked `[INFERENCE]`. **Section G** carries the
datasets you could not open, and the queries that found nothing with their log lines. Section C is
`not applicable to this prompt` except for the one-example-of-use rows.
