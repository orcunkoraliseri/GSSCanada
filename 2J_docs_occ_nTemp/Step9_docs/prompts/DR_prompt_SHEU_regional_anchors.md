# Deep-research prompt — DR-1: SHEU 2019 regional & dwelling-type anchor numbers

**Purpose.** Step 9 (light version) calibrates activity-driven equipment & lighting schedules so each
end use's **annual kWh matches NRCan statistics**, per **province × dwelling type**. The two prior
reports gave national figures + *derived* Quebec numbers; this prompt pulls the actual region- and
dwelling-resolved anchors we calibrate to. Paste the block below into a web-based deep-research LLM
(ChatGPT/Gemini deep research). Save the returned report into `Step9_docs/deepResearch/`.

```
You are doing deep research using authoritative Canadian energy statistics. I am calibrating a
residential building-energy model and need ANNUAL residential electricity end-use and appliance
consumption numbers, per HOUSEHOLD, broken down by PROVINCE and by DWELLING TYPE, from Natural
Resources Canada. Be precise and cite the exact source table for every value.

PRIMARY SOURCES (use these; cite table numbers + URLs):
- NRCan Survey of Household Energy Use (SHEU) 2019 summary + data tables:
  https://oee.nrcan.gc.ca/publications/statistics/sheu/2019/index.cfm
  https://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/menus/sheu/2019/tables.cfm
- NRCan Comprehensive Energy Use Database (CEUD) / Energy Use Data Handbook, Residential Sector,
  incl. provincial tables and the appliance Unit Energy Consumption (UEC) table.
- Hydro-Quebec residential electricity end-use breakdown (Quebec cross-check).
Conversion: 1 GJ = 277.78 kWh. Report kWh per household per year.

DELIVER (label EVERY value [Published] if read directly from a table, or [Derived] if computed —
and for [Derived] show the arithmetic, e.g. province total x a percentage split):

1) PROVINCE x END-USE table (annual kWh/household): provinces = Ontario, Quebec, British Columbia,
   Alberta, Prairies (Manitoba + Saskatchewan), Atlantic. End uses = space heating, water heating,
   space cooling, appliances, lighting. Also give each province's total household ELECTRICITY
   intensity (kWh/yr).

2) DWELLING-TYPE x END-USE table (annual kWh/household): single detached, attached / row / duplex /
   semi-detached, low-rise apartment, high-rise apartment, mobile. Same end-use columns.

3) APPLIANCE UEC table (annual kWh/yr), stock-average AND new, for: refrigerator, second
   refrigerator, freezer, dishwasher, clothes washer, clothes dryer, electric range/oven, and
   "other appliances & electronics". Include ownership/saturation rates by province and by household
   size where available.

4) ALWAYS-ON / BASELOAD components (the ones a behavioural model must hold flat): refrigerator +
   freezer + networking/standby. Give typical CONTINUOUS wattage (W), annual kWh, and their % share
   of the appliance block. Include any Canadian standby / phantom-load figures (and note US/IEA/LBNL
   fallbacks if Canadian data are thin).

5) LIGHTING annual kWh/household (and by province if available); and the APPLIANCES + LIGHTING share
   of (a) total residential energy and (b) the non-thermal electricity remainder (i.e. excluding
   space heating, space cooling, water heating).

OUTPUT FORMAT:
- Table A: Province x end-use (kWh/hh/yr) + total electricity intensity.
- Table B: Dwelling type x end-use (kWh/hh/yr).
- Table C: Appliance UEC (stock-average & new) + saturation.
- Table D: Baseload components (W continuous, kWh/yr, % of appliances).
- For each cell: [Published] (with exact table no. + URL) or [Derived] (with the arithmetic).
- Full citations (source, table number, URL, access date).
```
