# T26. Household travel surveys: when people leave home and when they return

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Household travel surveys record every trip each household member made on a survey day, with
departure and arrival times and the trip purpose, and the home is the first and last location. From
them the hours **away from home** follow directly. They are far larger than time-use surveys in most
regions (the Montreal origin-destination survey interviews tens of thousands of households; the
Greater Toronto survey is similar), they are regional rather than national, and several are public.
They could generate (`R1`) presence schedules, or constrain (`R2`) survey-generated ones by area. We
need to know which are obtainable, what they record, and whether anyone derived building occupancy
from them.

## What we need

### Item 1. The surveys

Data-source cards (brief section 9) for at least:

* Canada: Enquête Origine-Destination (Montreal, ARTM), Transportation Tomorrow Survey (Greater
  Toronto and Hamilton), and the regional surveys of Québec City, Ottawa-Gatineau (TRANS), Calgary,
  Metro Vancouver.
* United States: National Household Travel Survey (NHTS), and any large open regional survey.
* Europe: UK National Travel Survey, Germany Mobilität in Deutschland, France Enquête Mobilité des
  Personnes and the Île-de-France Enquête Globale Transport, Switzerland Mobility and Transport
  Microcensus, Netherlands ODiN, Spain (any national or Madrid regional survey), Italy (any national
  or Bologna regional survey).

For each, add: whether microdata or only tables are available; whether trip times are exact or
banded; whether trips at home (working from home) are recorded; household demographics shipped; the
spatial unit of the home location in the public file.

### Item 2. Presence from trips

Works that turned travel-survey trips into at-home presence schedules, for any purpose (energy,
exposure, epidemiology, transport). Section C rows with the method, the handling of people with no
trips, and any comparison with a time-use survey for the same place and year.

### Item 3. Travel survey against time-use survey

Studies that compared time out of home or trip counts between a travel survey and a time-use survey
of the same country. Report the direction and size of the difference; it is a known issue
(under-reporting of short trips). Quote the finding.

### Item 4. Building energy use

Works in building energy (residential or urban) that used travel surveys for occupancy. Section C rows.
`NOT FOUND` is possible; say what you searched.

## Named leads

ARTM, DMG (University of Toronto), NHTS portal, UK Data Service, MiD, SDES, Swiss Federal Statistical
Office, CBS and DANS (ODiN); *Transportation Research Parts A to D*, *Transportation*, *Journal of
Transport Geography*, *Travel Behaviour and Society*, *Energy and Buildings*, *Building and
Environment*.

## Hard constraints specific to this prompt

* Access for a university researcher in Québec is quoted for each Canadian survey; several are held by
  agencies and licensed per project.
* Sample sizes (households and persons) quoted from the survey's own documentation with the edition.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: can a Concordia researcher obtain Montreal origin-destination or Toronto
survey microdata with trip times, and has any building-energy study derived residential presence from a
travel survey.

**Section F** is item 1. **Section C** is items 2 and 4. **Section D** assesses "regional travel surveys
as a larger, local occupancy source than national time use" as a form of `A14`. **Section G** carries
item 3 and your negative controls.
