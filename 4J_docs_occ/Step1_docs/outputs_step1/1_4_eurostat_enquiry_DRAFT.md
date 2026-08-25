# Item 1.4 — Eurostat entity-recognition enquiry: READY-TO-SEND DRAFT

Status: **DRAFTED, NOT SENT.** Drafting is not the Definition of Done.
`Step1_docs/4thJ_01_corpusAcquisition.md:281` is explicit: *"the enquiry is sent to Concordia's
Office of Research and the date is recorded."* Only the author can send it, because it goes out in
the author's own name and asks Concordia, as an institution, to apply for a status. This file exists
so that the only remaining act is pressing send and writing the date on the line at the bottom.

Nothing downstream is blocked by it: no `G1.x` gate references item 1.4, and Step 1 was closed on
2026-08-16 with 1.4 explicitly outstanding and explicitly non-blocking.

---

## What is being asked, and why it is worth asking

Concordia is not currently on Eurostat's list of Recognised Research Entities. That fact is already
established and is **not** a substitute for having asked — the doc says so in those words.

Recognition under Commission Regulation (EU) No 557/2013 is what makes an institution eligible to
receive Eurostat Scientific Use Files. The file at issue is the **HETUS 2010 round**. Our three
national datasets (Spain, United Kingdom, Italy) *are* that round, so access would widen the corpus
from **three countries to seventeen with no harmonisation change at all** — the crosswalks,
the episode schema and the activity alphabet already built in Step 1 and Step 2 would carry over
unchanged.

That is the whole value of the enquiry. It is the only route that addresses **limitation C4**: with
three countries, leave-one-country-out trains on two, and the transfer claim in Step 6 is tested
against the thinnest possible donor pool.

Indicative timeline recorded in `DeepResearchPrompts/RL01_hetus_microdata_access.md`: roughly four
weeks for entity recognition, then eight to ten weeks for the research-proposal assessment. It will
not arrive in time for the current manuscript. It is filed for the work after it.

---

## The message to send

**To:** Concordia University, Office of Research (research services / data access contact)
**From:** Orcun Koral Iseri, Postdoctoral Fellow, Concordia University
**Subject:** Enquiry — Eurostat Recognised Research Entity status for access to HETUS microdata

---

Dear Office of Research,

I am writing to ask whether Concordia University holds, or would consider applying for, status as a
**Recognised Research Entity** with Eurostat under Commission Regulation (EU) No 557/2013.

I am a postdoctoral fellow working on building-energy and occupancy modelling. My current work uses
national time-use survey microdata to derive residential occupancy and activity schedules. I hold
the Spanish, United Kingdom and Italian national datasets of the 2010 Harmonised European Time Use
Survey (HETUS) round under their respective national licences, and the analysis is already running
on them.

Eurostat releases the HETUS 2010 round as a Scientific Use File covering seventeen participating
countries. Because the three datasets I already work with belong to that same round, access to the
Scientific Use File would extend the study from three countries to seventeen without any change to
the harmonisation already carried out. Methodologically this matters a great deal: the central
validation in my work holds one country out and trains on the remainder, and with three countries
that test is run against a very thin comparison pool. Seventeen would make it a real test.

My questions are therefore:

1. Does Concordia currently hold Recognised Research Entity status with Eurostat? If so, what is the
   internal procedure for a researcher to submit a microdata research proposal under it?
2. If not, is the Office of Research willing to submit the entity-recognition application (Form A,
   accompanied by the institutional documentation Eurostat requires)? I am glad to prepare the
   research-description material and to answer any methodological questions.
3. Who at Concordia would be the signing authority for the confidentiality undertakings that
   accompany a Eurostat microdata contract?

I am happy to provide a short project description, the data-management plan, and the licences under
which I currently hold the three national datasets.

Thank you for your time.

Kind regards,
Orcun Koral Iseri
Postdoctoral Fellow, Concordia University
orcunkoral.oseri@concordia.ca

---

## The line that closes item 1.4

Fill this in **after** sending, and copy the date into the Step 1 progress log:

```
SENT ON:            ____________________   (YYYY-MM-DD)
SENT TO:            ____________________   (name / address at the Office of Research)
REPLY RECEIVED ON:  ____________________   (or "no reply as of <date>")
OUTCOME:            ____________________
```

Until the first line carries a date, item 1.4 is **NOT DONE**, and the checklist must keep saying so.
