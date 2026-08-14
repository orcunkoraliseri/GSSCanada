# L13. From diaries to EnergyPlus in Europe: archetypes, schedule conventions, and activity-driven end-use loads

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C, E and F used.

## Why we are asking

Our previous three papers all ended in EnergyPlus. That is what makes them building-science papers
rather than data-science papers, and it is why they were published in building journals. Paper 4 must
keep that anchor or it becomes a machine-learning paper submitted to the wrong venue.

But the geography changes. Papers 2 and 3 used Canadian archetypes, the National Energy Code of Canada
for Buildings, and Canadian weather. Paper 4 is European, and we know almost nothing about the European
equivalents: which archetype library is the accepted reference, what the default occupancy and
appliance schedules are, and which standard governs them.

We also want to go beyond presence. A time-use diary records **what people are doing**, not merely
whether they are home. That drives appliance load, domestic hot water and lighting, which is a
substantially richer signal than an occupancy fraction. Our third paper opened this direction and we
want to carry it further.

## What we need

### Item 1. The European residential archetype landscape

For each of the following, one row: what it is, what it contains, spatial and typological coverage, the
file format, whether simulation-ready models are distributed or only parameter tables, the licence, and
a **direct download URL** in Section F.

1. **TABULA and EPISCOPE**, the European building typology project. We understand this is the standard
   reference for residential building typologies by country and construction period. Confirm, and say
   whether it distributes simulation-ready models or only U-values and geometry parameters.
2. **Hotmaps** and its building stock datasets.
3. The **EU Building Stock Observatory**.
4. National archetype libraries for the larger HETUS countries, especially Italy, since we already hold
   Italian microdata and it is the obvious first case study.
5. Any published set of **EnergyPlus or Modelica residential archetype models for Europe** that is
   directly downloadable and runnable. If none exists, that is an important finding and belongs in
   Section A.

### Item 2. The governing standards for occupancy and internal gains

1. Which standard governs **default occupancy, lighting and appliance schedules** for residential
   buildings in European energy calculations? We expect the EN ISO 52000 family and EN 16798-1 to be
   central, and possibly national annexes on top. Name the standard, the part, the year, and the table
   or annex where the schedules live.
2. **Transcribe the default residential occupancy schedule** from that standard: hourly or sub-hourly
   fractional values, per day type if the standard distinguishes them. This is the baseline our
   generated schedules replace or modulate, and we need it verbatim, with the table number.
3. Do the same for the default **appliance and lighting** gain profiles, and the default **metabolic
   rate** and occupant density assumptions.
4. How do these compare in structure with what we know from the North American side? Specifically: does
   the European standard give a single national profile, or profiles by dwelling type or household
   type? If it gives a single profile, then the diversity our model produces is precisely the
   contribution, and we want that stated with a source.
5. Is there a European equivalent of the reference-schedule critique literature, that is, published work
   measuring how far standard schedules are from observed behaviour? Those are our motivating
   citations.

### Item 3. Activity to end-use load: the conversion evidence

This is the scientifically richest item.

1. What published work maps **time-use activity codes to appliance events or power draws**? We are aware
   of a well-established lineage of high-resolution domestic demand models built from UK time-use data,
   and expect there to be more since. Map the field, with citations, and say which models are
   **openly available as code**.
2. For each mapping approach, what is the mechanism: an activity triggers an appliance with a
   probability and a duration, or an activity implies a power profile directly, or something else.
3. What appliance power and duration datasets exist for Europe, per country if possible, that we could
   use as the load side of the mapping? Include any open datasets of measured household appliance use.
4. **Domestic hot water**: what published profiles link time-use activities (washing, showering, food
   preparation, laundry) to draw volumes and profiles? Name the standard or the model, since DHW is
   often the dominant occupant-driven load in a well-insulated dwelling and our previous paper found a
   hot water plant to be a load-bearing part of the energy result.
5. Which of these mappings has been **validated against measured aggregate demand**, and at what
   spatial and temporal scale? A mapping that has never been validated is a caveat, not a method.

### Item 4. Schedule injection conventions

1. What is the accepted way to express a generated occupancy schedule in EnergyPlus for a residential
   model: `Schedule:Compact`, `Schedule:File`, or something else, and at what timestep? Our previous
   work used 30-minute `Schedule:Compact` per day type per climate zone, which is compact but coarse;
   is there a documented reason to prefer per-dwelling `Schedule:File` at finer resolution, beyond file
   size?
2. What is the correct treatment of **occupant count versus occupied fraction**? Our residential channel
   replaces the schedule and sets the number of people from household size, while our commercial
   channels modulate a code density. State the accepted convention for residential European models and
   its source.
3. How is **interpolation to timestep** meant to be handled, and what does it do to a schedule derived
   from a discrete activity sequence? A step-wise presence signal interpolated linearly is no longer
   the signal we generated, and we want the standard practice named.

### Item 5. The scale question

Our claim is UBEM-relevant. So:

1. What UBEM tools accept per-building or per-dwelling occupancy schedules as an input, and in what
   format? Name the open ones with URLs.
2. Is there a published European UBEM case study that used **time-use-derived** schedules, at city
   scale? If yes, that is our closest comparator and it belongs in `L14`'s novelty matrix as well.
3. What is the reported **sensitivity of annual energy and peak demand to occupancy schedule choice** in
   European residential stock studies? A number here is the strongest possible motivation sentence for
   the paper's introduction, so please try hard to find measured values, with the study design that
   produced them.

## Named leads

The TABULA and EPISCOPE project sites and their national typology brochures; Hotmaps project outputs;
the EU Building Stock Observatory; EN ISO 52000, EN 16798-1 and their national annexes; the IEA EBC
Annex 66, 79 and 87 outputs on occupant behaviour; the high-resolution domestic electricity demand
modelling literature; open datasets of measured household electricity and appliance use in Europe;
`unmethours` and the EnergyPlus Input Output Reference for the schedule object conventions; published
European UBEM platforms and their documentation.

## Hard constraints specific to this prompt

* **Transcribe standard schedule tables verbatim** where you can open them, with the table number and
  edition. Do not paraphrase a schedule into prose.
* Standards are often paywalled. If you cannot open EN 16798-1, say `COULD NOT OPEN` and do not
  reconstruct its tables from a secondary description, however confident the secondary source sounds.
  A wrong baseline schedule would silently corrupt every downstream comparison.
* Keep **as-simulated** and **measured** strictly separate and separately labelled, as our earlier
  research rounds established.
* Give direct file URLs in Section F, not programme homepages.

## Deliverable

**Section B** carries the transcribed standard schedules and the sensitivity numbers from item 5.

**Section C** carries the recommended archetype source and injection convention.

**Section F** is the downloadable-artefact catalogue: archetype libraries, appliance datasets, UBEM
tools.

**Section G** carries the validation status of each activity-to-load mapping, and your negative
controls.
