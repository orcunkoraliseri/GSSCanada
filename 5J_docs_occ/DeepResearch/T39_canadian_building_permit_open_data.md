# T39. Canadian building-permit open data as text a model can read

Paste `00_MASTER_BRIEF.md` first (read its section 10), then `_RESPONSE_TEMPLATE.md`, then this
prompt, in one fresh session. Run alone. Written 2026-09-22. Your files are `RT39_canadian_building_permit_open_data.md`
and `RT39_pages.log`.

## Why we are asking

The fifth paper needs building-permit records whose free text says what work was done to a home, so
that a language model can infer heat pumps, air conditioning, insulation and window replacement
(brief section 10, role `L1`). We are checking Montreal and Toronto ourselves. We need to know which
other Canadian permit files exist, what their text fields hold, how far back they go, and whether the
text is rich enough to read.

## What we need

### Item 1. Municipal permit files, city by city

One record-source card (brief section 10) for each of: Montreal (all boroughs), Toronto (every permit
file it publishes: active, cleared, and any HVAC or mechanical permit file), Vancouver, Calgary,
Edmonton, Ottawa, Winnipeg, Quebec City, Laval, Gatineau, Longueuil, Sherbrooke, Mississauga, Brampton,
Hamilton, London (Ontario), Kitchener, Waterloo, Surrey, Burnaby, Victoria, Halifax, Regina, Saskatoon.
A city that publishes no permit file gets a `NOT FOUND` line with the URLs tried.

For each card also give, from a logged download of the first rows or the data dictionary:
* the exact name of every free-text field, and three verbatim example values from residential rows;
* the date range of the rows, and the row count shown on the portal;
* whether a permit for a heat pump, a central air conditioner, insulation or windows is required in
  that city at all, quoted from the city's own permit guidance page (if it is not required, the file
  cannot show it).

### Item 2. Provincial and other public permit or licence records

Cards for any province-wide public record that shows mechanical, electrical, gas or refrigeration work
on homes: for example Quebec's RBQ or CMEQ, Ontario's Electrical Safety Authority or TSSA, BC's
Technical Safety BC, Alberta's safety codes records. Say plainly if a record exists but is not public.

### Item 3. Who has already used Canadian permit text

Studies or reports that used the free text of a Canadian permit file, for any purpose. Section C rows
with: the city, the years, the fields used, the method (keyword rules, classic text classifier,
language model), what was extracted, and the reported accuracy against any truth. `TITLE ONLY` where
no abstract or text was logged.

## Named leads

City open-data portals (donnees.montreal.ca, open.toronto.ca, opendata.vancouver.ca,
data.calgary.ca, data.edmonton.ca, open.ottawa.ca, and each city's own portal); open.canada.ca;
Données Québec (donneesquebec.ca); municipal permit guidance pages; OpenAlex queries on "building
permit" with "Canada", "text mining", "natural language processing", "retrofit", "heat pump".

## Hard constraints specific to this prompt

* A portal counts only if you reached the dataset page and a download, API or preview of its rows.
  Report the file format, the date of the most recent row you saw, and the log line.
* Field names and example values are copied from the logged rows, never described from memory.
* Do not rank cities by how useful they are; report the cards. The manager judges.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which Canadian cities publish residential permit records with a free-text
description field, how many years each covers, and in which language. **Section F** is items 1 and 2.
**Section C** is item 3. **Section D** says, as `[INFERENCE]`, which heat-pump, air-conditioning,
insulation and window work is likely invisible in these files because no permit is required.
**Section G** carries the `NOT FOUND` lines, the pages you could not open, and your negative controls.
