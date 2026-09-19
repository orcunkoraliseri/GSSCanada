# T22. Occupancy inferred from smart meters: the methods, the accuracy, the open data

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Smart meters record whole-home electricity every 15 to 60 minutes (sometimes every second) for
millions of homes. A body of work infers from them whether someone is home. If that inference is
accurate enough, smart-meter data is a presence source at a scale no survey reaches, and it could
constrain (`R2`) or validate (`R3`) generated schedules. We need to know how accurate the inference
is against ground truth, and which meter datasets are open to us, especially ones that come with a
household survey.

## What we need

### Item 1. Inference methods and their measured accuracy

Every 2012 to 2026 work that infers occupancy or presence from aggregate household electricity (or
from disaggregated loads, NILM). Section C rows with: method (threshold, HMM, clustering, supervised
learning, deep learning), data resolution, number of homes, **the ground truth used and the reported
accuracy metric and value**, and whether accuracy held across homes not used in training. Report the
best and the typical accuracy, and at which resolution accuracy collapses (for example 30- or
60-minute data).

### Item 2. Meter datasets with a household survey

Data-source cards (brief section 9) for meter datasets that ship with household characteristics or
occupancy questions. At least: the Irish CER Smart Metering Trial (ISSDA), Low Carbon London, the
UK Smart Energy Research Lab (SERL), Pecan Street, the Ausgrid Solar Home dataset, the London
Datastore household sets, Ontario and Québec Green Button or utility research releases, and any
Canadian utility dataset available to university researchers. Say for each whether the survey has
a question on time at home, number of occupants, or work pattern.

### Item 3. Occupancy-relevant findings from meters

Studies that used meter data to describe **when homes are occupied** at population level (for example
the shift in daytime load after 2020, clusters of daily load shape linked to household type). Report
only measured comparisons. Say whether any compared a meter-derived presence share with a time-use
survey for the same country and year.

### Item 4. Can meter data generate schedules?

Has anyone generated synthetic occupancy schedules from meter data (not synthetic load), and used them
in a building energy simulation? `NOT FOUND` is expected to be possible; say what you searched.

## Named leads

ISSDA; UK Data Service and SERL portal; London Datastore; Pecan Street Dataport; Ausgrid; Green Button
Alliance; *Applied Energy*, *Energy and Buildings*, *IEEE Transactions on Smart Grid*, *Energy
Informatics*; BuildSys and e-Energy proceedings; NILMTK documentation.

## Hard constraints specific to this prompt

* An accuracy number is reported only with its ground truth named. "Occupancy accuracy 90 percent"
  with no ground truth is not admitted.
* Separate presence inference from activity or appliance disaggregation; do not merge the two
  literatures.
* SERL and CER access rules quoted with the date; state whether a researcher outside the UK or
  Ireland is eligible.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: how accurate is presence inference from 30- or 60-minute meter data
against ground truth, and which open meter dataset with a household survey a Canadian researcher can
obtain today.

**Section C** is items 1 and 3. **Section F** is item 2. **Section D** assesses "meter-derived presence
as a constraint on time-use occupancy" as a form of `A14`. **Section G** carries item 4 and your
negative controls.
