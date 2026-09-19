# T20. Smart thermostats as measured presence: ecobee Donate Your Data and its peers

> **Corrections 2026-09-18 (round 2).** Round 1 of this prompt failed vetting: invented co-authors,
> quotes that are not on their pages, named items dropped without a word, and no page opened. These
> rules add to everything below and win where they differ.
> * Paste the CrossRef-returned title beside every DOI in every table row.
> * A row without a resolving identifier (DOI, arXiv ID, or a landing page you opened) is not admitted.
> * Our own papers' rows are copied verbatim from brief section 2; never give one a title yourself.
> * Author list, year, volume and pages are pasted from the same CrossRef record
>   (`api.crossref.org/works/<DOI>`), never typed. If CrossRef lists two authors, you list two.
> * Every page you open, CrossRef and OpenAlex calls included, gets a line in `RT<NN>_pages.log`
>   (format in the runner). Every quote, variable name, licence, count and URL in the report must be
>   traceable to a log line. A claim with no log line is not admitted.
> * Every item and every named source below gets its own heading or card. If you could not find it,
>   write `NOT FOUND` and list the URLs you tried; they must be in the log.
> * Known prior work, supplied by us and therefore not a finding: Doma, Prajapati and Ouf 2024,
>   *Building and Environment* 261, 111713, compared ecobee occupancy with the Canadian Time Use
>   Survey. Item 2 must say, from its full text if you can open it, whether that comparison went
>   beyond total daily occupied hours (by hour of day, by household or dwelling type, first departure
>   and last return). If the full text does not open, write `COULD NOT OPEN`.
> * Item 1: Resideo gets its own card; the Québec and Texas demand-response programmes each get a
>   card or `NOT FOUND`; Zenodo, Dryad, Figshare and NREL OEDI are each searched with the query logged.
> * Describe the ecobee access route only as its own page states it. No process, fee or turnaround
>   that the page does not show.
> * Every Section C row states the study type (results, protocol, review). A protocol has no findings.

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Smart thermostats with remote occupancy sensors record motion in thousands of North American homes,
many of them in Canada, at five-minute resolution, for years. If a researcher at a Canadian university
can obtain such data, it is the closest thing to **measured residential presence at population scale**
that exists, and it could validate (`R3`) or constrain (`R2`) the presence our time-use generators
produce. We need to know what exists, who can get it, what it really measures, and what the field
has already done with it.

## What we need

### Item 1. The datasets

For each program or dataset below, the full data-source card of brief section 9, plus: number of homes
and number in Canada by province if stated; years; the exact sensor variables (thermostat motion,
remote-sensor occupancy, setpoint, mode, runtime, indoor and outdoor temperature, humidity); how
"occupancy" is defined by the vendor (motion within a window, a hold, a smart-home or away mode);
what household metadata ship with it (floor area, age of home, number of occupants, province or
postal region); the application process, turnaround and fee if any, quoted.

1. ecobee Donate Your Data (DYD).
2. Any Google Nest, Honeywell Resideo or other vendor research-data program.
3. Utility demand-response programs that published thermostat data (for example in Ontario, Québec,
   California, Texas).
4. Any public-domain subset or derived open dataset built from these (for example on Zenodo, Dryad,
   Figshare, NREL OEDI).

### Item 2. What has been done with them

Every 2016 to 2026 work that used smart-thermostat data to **infer presence or occupancy schedules**,
build occupancy models, compare with time-use surveys, or estimate energy impacts of occupancy.
Section C rows with: homes used, region, the occupancy definition adopted, whether the result was
compared against a survey or a standard schedule, and the size of any reported difference. Say which
used Canadian homes.

### Item 3. What the sensor misses

Evidence on the measurement validity of thermostat occupancy: sleeping occupants read as absent,
sensor placement, pets, multiple occupants read as one, false vacancy. Any study that ground-truthed
thermostat occupancy against another measurement. Quantify if the literature does; say `NOT FOUND` if
not.

### Item 4. Selection bias

Who owns a smart thermostat and who donates data: income, tenure, dwelling type, heating fuel,
household composition. Any study that reweighted DYD homes to a census. Say whether renters,
apartments and low-income households are represented at all.

## Named leads

ecobee DYD program page and its data dictionary; NREL OEDI; Natural Resources Canada and utility
reports; *Energy and Buildings*, *Building and Environment*, *Applied Energy*, *Energy*,
*Journal of Building Performance Simulation*; BuildSys and e-Energy proceedings.

## Hard constraints specific to this prompt

* The eligibility and licence of DYD are quoted from the program's own page with the date checked.
  Say whether derived schedules may be published.
* Do not describe motion events as "occupancy" without the vendor's own definition quoted beside it.
* Do not count a thermostat study as an occupancy study if it only analysed setpoints.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: can a Canadian university researcher obtain thermostat presence data
today, for how many Canadian homes, and has anyone already compared it with a national time-use
survey.

**Section C** is item 2. **Section F** is item 1, one card per dataset. **Section D** assesses `A14` in
the form "thermostat presence as validation for time-use occupancy", taken, partly or open.
**Section G** carries items 3 and 4 and your negative controls.
