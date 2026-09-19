# T24. Aggregated mobile-phone mobility as a signal of time at home

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run in wave 6, after `T19`.

## Why we are asking

Since 2020, several organisations have published aggregated mobility statistics derived from phones:
the Google COVID-19 Community Mobility Reports carried a "residential" category measuring change in
time spent at places of residence; Meta Data for Good published movement and stay-put measures;
Spain's statistical institute and transport ministry published hourly origin-destination matrices from
operator data; Eurostat and several statistical offices ran mobile-positioning pilots. These are
aggregate and area-based, never per household. They could constrain (`R2`) the share of people at
home by hour and area, and record change over time (`R4`). We need to know what is published, what it
actually measures, and whether the building-energy field has used it.

## What we need

### Item 1. The sources

Data-source cards (brief section 9) for at least:

1. Google COVID-19 Community Mobility Reports: the residential metric's definition quoted, its
   baseline, geographies for Canada, Spain, Italy and the UK, years, whether still downloadable.
2. Apple Mobility Trends Reports.
3. Meta Data for Good: movement range maps, colocation maps, and any successor product.
4. Spain: INE mobile-phone mobility study and the transport ministry (MITMA or its successor) open
   big-data mobility study; hourly resolution and areas.
5. Italy, UK, France: any official statistics built from mobile network data (Istat, ONS, INSEE).
6. Eurostat mobile network operator data pilots and any published indicators.
7. Canada: Statistics Canada or any provincial body publishing mobility or presence indicators from
   phone data; say `NOT FOUND` if none.
8. Commercial panels with academic access (for example Advan, SafeGraph successors via Dewey,
   Spectus, Veraset): access terms quoted, and whether a Canadian university can obtain Canadian or
   European coverage.

### Item 2. What "at home" means in each

How each provider infers home location and time at home (night-time dwell, ping clustering), the
minimum population thresholds and noise added for privacy, and known biases (phone ownership, device
sharing, app users). Quote the methodology notes.

### Item 3. Use in building energy

Works that used any of these sources for building occupancy, residential energy demand, or to adjust
occupancy schedules (including COVID-period studies). Section C rows. Say whether any compared the
mobility "residential" signal with a time-use survey or with measured home presence.

### Item 4. Hourly shape

Which sources give an hour-of-day profile of presence at home (not only a daily change against a
baseline)? This decides whether they can constrain a 48-slot schedule or only a daily total.

## Named leads

Google, Apple, Meta and INE methodology pages; Spanish open mobility study portal; Eurostat
experimental statistics; *Nature Communications*, *EPJ Data Science*, *Scientific Data*,
*Transportation Research Part C*, *Energy and Buildings*, *Applied Energy*; Flowminder and UN
Global Platform documentation.

## Hard constraints specific to this prompt

* Quote each metric's definition. Google's residential category is a change against a pre-2020
  baseline, not a share of time; do not treat it as a share.
* State for every source whether it is still updated or frozen, with the last date covered.
* No proposals to buy or scrape individual traces. Aggregates only.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: which open mobility source gives an hour-of-day at-home profile by area
for Canada or for Spain, Italy and the UK, and whether any building-energy study used such a profile
to constrain occupancy.

**Section F** is item 1. **Section C** is item 3. **Section D** assesses "phone-derived at-home profiles
as a calibration target for time-use occupancy" as a form of `A14`. **Section G** carries items 2 and 4
and your negative controls.
