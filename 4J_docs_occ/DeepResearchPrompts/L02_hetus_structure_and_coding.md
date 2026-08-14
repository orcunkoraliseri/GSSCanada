# L02. The HETUS data model: file structure, activity coding list, location and co-presence fields, and where countries diverge

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, D and E are used lightly; Section F is required.

## Why we are asking

Whatever model we build, its **input and output alphabet is the HETUS coding scheme**. We cannot design
a serialisation, a token vocabulary, or a validity constraint without knowing exactly what the codes
are, how many there are at each hierarchical level, and what the diary record looks like on disk.

Our published Italian work used a 145-class activity target derived from the ISTAT diary, aggregated
from the ISTAT implementation of the harmonised coding. We do not know how cleanly that maps onto the
HETUS Activity Coding List as Eurostat defines it, or whether the 2008-guideline coding and the
2018-guideline coding are the same list.

This prompt is a **transcription and structure** prompt. It asks for documentation, not for judgement.

## What we need

### Item 1. The Activity Coding List, at each level

1. Name the governing document and edition for the ACL used in each HETUS wave. If the coding list
   changed between the 2008 guidelines and the 2018 guidelines, say what changed at the top level.
2. Give the **complete top level** of the ACL verbatim: the one-digit or two-digit major groups with
   their official labels. This is a short list and we want it exactly as published, not paraphrased.
3. State **how many codes exist at each hierarchical level** (major groups, then the two-digit level,
   then the three-digit level if one exists). Give the count as a number, per level, per edition.
4. State whether **secondary activities** are coded on the same list as primary activities.
5. Identify the codes that correspond to what a building energy modeller cares about: sleeping,
   food preparation, eating, personal care and washing, television and computer use, laundry and
   household upkeep, and travel. Give the code and the official label for each. We need these because
   they drive appliance and domestic hot water loads downstream, not merely presence.

### Item 2. The location field, verbatim

Our entire multi-channel work in the previous paper keys off the **location code**, because location is
what says whether a person is at home, at their workplace, in a shop, or in transit. In Canadian GSS
the equivalent field changed coding between cycles and cost us real effort.

1. Transcribe the **complete HETUS location code list** with official labels, per edition.
2. State whether location is recorded for **every slot** or only when it changes.
3. State whether "at home" is a single code or splits (for example, dwelling versus own garden or
   grounds), because that distinction decides whether presence in the conditioned volume is
   recoverable.
4. Say whether a **transport mode** is coded separately from location, and if so, transcribe that list
   too.

### Item 3. The co-presence field, verbatim

1. Transcribe the **"with whom" code list** with official labels, per edition.
2. State whether it is one field or several parallel yes-no fields (with partner, with children, with
   other household members, with people outside the household).
3. State whether the codes distinguish **household members from non-household members**. Our published
   work flags co-presence handling as the source of load overestimation when shared activities are
   counted independently, so this field is load-bearing for us.

### Item 4. The physical file structure

1. Confirm or correct our understanding that a HETUS delivery comprises **three linked files**:
   household, individual, and time-use diary. Name each file as the documentation names it, and give
   the linking key or keys.
2. For the diary file, state the record shape: **one row per slot, one row per episode, or one row per
   diary day with wide slot columns**. If it varies by country or wave, say so and give an example of
   each.
3. Give the **weight variables**: their names, what population each inflates to, and whether there are
   separate individual weights and diary-day weights. If a diary-day weight exists that corrects for
   the over- or under-representation of particular day types, name it explicitly. Prompt `L09` builds
   on this.
4. State whether the files carry a **country identifier** in a harmonised delivery, or whether each
   country arrives as a separate file set.

### Item 5. Where countries actually diverge

The Eurostat framing is that HETUS is harmonised. Our experience with supposedly harmonised survey
series is that the divergences are where the work is. Please document them rather than reassure us.

For each of the following, say whether it is uniform across participating countries or varies, and if
it varies, name at least two countries that differ and how:

1. Diary slot length and number of slots per day.
2. Number of diary days per respondent, and whether the days are consecutive.
3. Minimum respondent age.
4. Whether the diary starts at midnight or at another hour. Our own pipelines use a 04:00 origin
   internally, so we need to know the source convention.
5. Which optional modules or optional variables a country may omit.
6. Fieldwork spread across the year, and whether all seasons are covered in every country.
7. Whether the collapsing of activity codes to a coarser level is done nationally before delivery.

### Item 6. Documented crosswalks to other time-use surveys

Has anyone published a **crosswalk between the HETUS ACL and the American Time Use Survey coding**, or
between HETUS and the MTUS harmonised activity list, or between HETUS and the Canadian GSS time-use
activity codes? If such a crosswalk exists as a retrievable file, that is a high-value artefact for us
and belongs in Section F with a direct URL. If none exists, write `NOT FOUND` and say what you searched.

## Named leads

The Eurostat *Harmonised European Time Use Surveys* guidelines editions and their annexes, which is
where the coding lists live; Eurostat's HETUS methodological manual and quality reports; national
statistical institute HETUS implementation reports, which often reprint the code lists in a national
language alongside the harmonised codes; the Centre for Time Use Research documentation for MTUS,
which documents its own harmonised activity list and may document the mapping; IPUMS Time Use
documentation for ATUS coding.

## Hard constraints specific to this prompt

* **Transcribe, do not summarise.** A code list rewritten in your own words is useless to us, because
  we will write code against these strings. Carry the code, the official label, the edition, and the
  table or annex number.
* If a list is too long to transcribe in full at the deepest level, transcribe the top two levels in
  full and give the count and the source location for the deepest level. Say which you did.
* **Do not fill a gap by reasoning from another survey.** If the HETUS location list is not available
  to you, do not substitute the ATUS "where" list and call it HETUS. That specific substitution would
  be very hard for us to detect and would poison the design.
* Report no model architecture opinions in this prompt. This one is about the data only.

## Deliverable

**Section B** carries the transcriptions: the ACL top level, the location list, the co-presence list,
the weight variable names, each as its own block with its edition and source location.

**Section F** carries the retrievable documents: every guidelines edition, every annex, every codebook,
with direct URLs.

**Section G** carries the divergence table from item 5, and the crosswalk verdict from item 6.
