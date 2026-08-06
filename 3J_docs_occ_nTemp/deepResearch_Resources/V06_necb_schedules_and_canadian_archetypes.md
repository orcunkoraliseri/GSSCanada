# V06. NECB schedule tables and Canadian archetype artefacts: locate the documents, do not report EUI values

Paste `00_MASTER_BRIEF_V2.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D, E and F are **not used** in this prompt; write `not applicable to this prompt` under each.

This prompt is deliberately shaped against the failure mode of the five rounds before it. **It asks for
exactly one class of number, from one named table, and forbids every other number.** Section B will be
short or empty, and that is the intended outcome. Section G and Section H are the deliverable.

## Why we are asking

Five rounds have come back (`RV01` to `RV05`). Every one contained figures that did not survive an
offline arithmetic check, and every check was run before any value entered our documents. We are not
telling you this to be adversarial. We are telling you because it changes what we are asking for.

What the previous rounds got **right**, consistently and independently, was **document identity**:
which report number carries which real title, which named document does not exist. `PNNL-28543` was
resolved twice, by two separate rounds, to a nuclear fuel characterisation report, and that answer held
up. That is a real result and it closed a question for us.

What the previous rounds got **wrong**, every time, was **values**. The most recent round returned
sixty rows of per prototype per climate zone EUI. Checking them locally:

* All twelve of its ASHRAE 90.1-2004 anchor rows equalled, to two decimal places, a table we already
  hold, but carried the **wrong representative cities** for that table's lineage. The values were
  right and the provenance was impossible, which is the signature of a table that was reconstructed
  rather than opened.
* Its EnergyPlus end use blocks summed to between **6 %** and **97 %** of the totals they were printed
  against. An `End Uses` table sums to Total Site Energy by construction, so no block could be genuine.
* The **colder** of the two climate zones used **less** energy in five rows, with space heating
  intensity itself inverted, in a report that had been warned in advance that this exact inversion had
  occurred before.
* Retail energy intensity got **60 % to 94 % worse** as the code edition tightened.

So: **we no longer accept EUI values through this channel.** We can retrieve those ourselves from the
published model packages. What we cannot easily do ourselves is establish whether a particular document
or dataset exists and where its file lives. That is what this prompt asks.

Two questions remain, and both are locate the artefact questions.

## What we need

### Item 1. The NECB occupancy schedule for retail or mercantile occupancies, transcribed from the table

This is the **only** place in this prompt where a number is wanted.

Our injected building models contain exactly one NECB schedule set, the one named `NECB-A-Occupancy`
in the IDF, whose weekday profile peaks at **0.95** and dips to **0.50** across 12:00 to 14:00. That
midday dip is a lunch trough, which is office behaviour and the opposite of retail behaviour. A
constant of `0.95` has been used in our retail channel and was described in our documentation as the
NECB retail or sales peak fraction. On checking, it is not: it is the office schedule's peak, inherited
because no retail schedule set is present in the model at all. We have already corrected our
documentation to say so. We now want to know what the correct value is.

Please:

1. Identify **which NECB schedule type letter** the National Energy Code of Canada for Buildings
   assigns to retail, mercantile or sales occupancies, in the **2017** edition and in the **2020**
   edition. Name the edition, the table number, and the page.
2. Transcribe the **fractional occupancy schedule** for that schedule type: all twenty four hourly
   values, for each day type the table distinguishes (weekday, Saturday, Sunday and holiday, or
   whatever partition the table actually uses). Transcribe it **verbatim from the table**. Do not
   smooth, do not interpolate, do not fill a missing hour.
3. Do the same for the **lighting** fractional schedule of that same schedule type, which is what our
   retail lighting diversity work needs.
4. State the **peak value** of the occupancy schedule explicitly, as its own sentence, since that is
   the single constant our model uses.
5. If the schedule tables are in a **referenced** document rather than in NECB itself, for example an
   ASHRAE 90.1 appendix or a National Research Council supplementary table set, say which document and
   give its identifier. NECB's schedule sets have historically been aligned with 90.1 Appendix G or
   with the older ASHRAE 90.1-1989 schedule sets, and if that is the actual provenance we want to know,
   because it changes what we can claim.

**How this will be checked.** We hold the injected IDF and can read `NECB-A-Occupancy` byte for byte.
If your answer for schedule type A does not reproduce a 0.95 peak with a 0.50 midday dip on weekdays,
your transcription is wrong and we will discard the whole item. **Please transcribe schedule type A as
well, for exactly this reason.** It costs you one extra table and it is the only way we can trust the
retail one. If you cannot open the table, say `NOT FOUND` for both and do not reconstruct either from
memory or from a secondary description.

### Item 2. Does an as modelled Canadian archetype energy dataset exist as a retrievable file?

Our buildings are **NECB 2017 compliant, in Montreal (climate zone 6A) and Calgary (climate zone 7)**.
Every reference band we currently hold traces back to the American DOE prototype lineage at ASHRAE
90.1-2004 vintage, which is both the wrong code and the wrong country. A previous round was asked to
find a Canadian replacement and returned a CanmetENERGY archetype study that does not exist, plus a
report number that turned out to be a nuclear fuel document.

We are **not** asking you for Canadian EUI values. We are asking whether the artefact exists.

For each of the leads below, answer three questions and only these three:

* **Does it exist?** Give the real title, issuing body and year, or write `DOES NOT EXIST` with the
  search terms you used.
* **Where is the file?** A URL that resolves **directly to a downloadable file or to a dataset landing
  record with a download control on it**. A programme homepage, a search results page or a news
  release is not an answer, and the row should read `NO RETRIEVABLE FILE` instead.
* **What is in it, structurally?** Does it contain simulated annual energy results per archetype per
  location, yes or no. If yes, say what the unit and area basis are and how many archetypes and
  locations it covers. **Do not report any of the values.**

Leads to work through, each as its own row:

1. **CanmetENERGY Ottawa** building archetype or reference building model sets, in any year, including
   anything distributed with the CAN-QUEST or HOT2000 tool families.
2. **Natural Resources Canada** open data portal (`open.canada.ca`) for NECB reference building or
   archetype simulation datasets.
3. The **National Research Council of Canada** codes publications, for any technical documentation
   supporting NECB 2017 or NECB 2020 that carries modelled energy results, for instance a cost
   effectiveness or energy impact analysis published alongside the code edition.
4. **BC Energy Step Code** metrics research reports, and the **Toronto Green Standard** modelling
   backgrounders, both of which are known to publish modelled EUI targets by archetype for Canadian
   climate zones.
5. **CBECS' Canadian counterpart**, the NRCan Comprehensive Energy Use Database and the Commercial and
   Institutional Consumption of Energy Survey (CICES). State clearly whether these are **metered
   survey** data rather than as modelled, because that distinction decides whether they can be
   compared with a simulation output at all.

If the honest answer across all five leads is that no as modelled Canadian archetype dataset is
publicly retrievable, **say that in the first sentence of Section A**. That is a complete answer and it
closes the question for us. It is worth more than a table we cannot open.

### Item 3. Your own negative controls

At the end of Section G, answer these two questions in plain sentences:

1. **Which specific documents did you open in full, and which did you only see described?** List them
   separately. If the count of documents you opened in full is zero, say zero.
2. **What would have caused you to write `NOT FOUND`?** Name the condition. A report that never
   reaches a `NOT FOUND` under any circumstance is a report that cannot fail, and we have received
   several.

## Named leads

`nrc-cnrc.gc.ca` publications and the Codes Canada catalogue for NECB 2017 and NECB 2020;
`natural-resources.canada.ca` and `open.canada.ca` for CanmetENERGY datasets;
`oee.nrcan.gc.ca` Comprehensive Energy Use Database; the BC Housing and BC Energy Step Code research
library; the City of Toronto Green Standard technical resources; ASHRAE 90.1 Appendix G schedule sets
and the ASHRAE 90.1-1989 schedule tables, as the historical origin of many NECB schedule sets.

## Hard constraints specific to this prompt

* **Report no energy intensity value of any kind.** Not for a prototype, not for an archetype, not for
  a climate zone, not in kWh/m2, kBtu/ft2, GJ or MJ. The only numbers permitted in this entire report
  are the fractional schedule values in item 1, which lie between 0 and 1. Any energy intensity figure
  appearing anywhere in your answer causes us to discard the report unread. This constraint exists
  because we can retrieve those values ourselves and five rounds have shown that this channel cannot.
* **Do not state, estimate or reproduce any output of our model.** You cannot see our results.
  Anything you say about them is either copied from this prompt or invented, and in two previous rounds
  it was invented.
* **Do not propose changing any band, threshold or gate.** Not the office floor, not the hotel ceiling,
  not the retail band. Three of the previous five rounds proposed a change that happened to make our
  failing test pass, after being told in writing not to. We read that pattern as a signal about the
  report, not about the evidence.
* **Carry the metadata with the number.** When you transcribe a table, carry its edition, its table
  number, its page and its column headings across with it. The most recent round's fabrication was
  invisible at the value level and only surfaced because the city labels attached to the values
  belonged to a different document lineage. **Provenance is what we check first now.**
* **Do not mark anything "read full text" unless you opened that specific file.** A landing page, an
  abstract, a search snippet or a cached summary is not the full text, and saying so plainly costs you
  nothing with us.

## Deliverable

**Section B**: the item 1 schedule transcriptions only, one row per schedule type per day type per
hour, or a compact twenty four column table per day type, whichever is cleaner. Nothing else goes in
Section B. If item 1 could not be retrieved, Section B reads `NOT FOUND` and that is acceptable.

**Section G**: the item 2 artefact table, five rows, one per lead, with the three columns described
above; every URL that failed to resolve; and the item 3 negative controls.

**Section H**: for each document, title, issuing body, year, edition, identifier, the URL you opened,
and an explicit statement of whether you read the full text, read only a summary, or could not open it.

We would rather have one schedule table we can check against our own IDF and five honest
`DOES NOT EXIST` rows than a complete looking report we have to falsify ourselves for the sixth time.
