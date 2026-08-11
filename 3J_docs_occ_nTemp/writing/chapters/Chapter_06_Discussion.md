# 6 Discussion

Inside one envelope, on one plant, the four populations do not behave as one occupant. They peak at
different hours, hotel at 18.91 h against a midday cluster of 11.90 to 12.37 h, and the whole-building
peak at 14.95 h coincides with none of them. Weekday day-to-night structure differs by an order of
magnitude and in one case by sign, from retail's 34 to 1 to residential's 3.9 to 1 and hotel's outright
inversion. Because the peaks fall apart, the whole-building coincidence factor stays below 1 in every
cell, median 0.941: use-type diversity attenuates the aggregate peak as household diversity does inside a
single archetype. A single-channel schedule cannot carry a difference between populations.

The architecture is what makes that observation available. One model trained jointly to output four
independent presence channels, dispatched through a per-space exact-match routing key, lets one tower
carry households, a workforce, customers and guests each on its own signal, with the decode-time
exclusivity projection keeping them from colliding before the building model. The design is additive on
the two-channel construction stage in a demonstrable sense, a missing channel falling back to the
untouched code baseline. Bit-identity of the residential and office outputs across stages is not claimed:
five of the nine steps carry no cross-stage comparison, and Table 6 says so in place of a verdict.

The office channel fails its energy-use-intensity gate in all 56 cells, and the natural reading, that the
model under-predicts office demand, is not what the evidence supports. The strongest piece is a control
the model never touches: the uninjected reference implementation, carrying no occupancy signal at all,
scores 85.45 against the same 100 kWh/m2/yr floor, failing by 15 % before this study contributes a single
schedule. Two mechanisms that would put the model rather than the band at fault were refuted across the
cell set: measured heating share is about 17 % against the band's implied 35 to 45 %, in the wrong
direction to close the gap, and re-basing on service and mechanical area moves every cell further down.
The band's own source document states three different floors for itself. Nothing was moved: the floor
stays at 100 and all 56 cells stay FAIL, median 71.02 kWh/m2/yr.

Hotel fails differently, and the geometry of the failure is itself informative. The 56 measured
intensities form two disjoint clusters tracking the tower prototype and nothing else: 28 cells at 203.33
to 218.22 kWh/m2/yr, comfortably inside the band, and 28 at 302.86 to 318.42, entirely above the 300
ceiling. The largest gap between consecutive values falls exactly between them, 84.64 kWh/m2/yr, 70.5 %
of the band's own width, with the ceiling inside it. A ceiling placed anywhere in a gap that wide splits
the cells the same way, so the gate cannot distinguish correct hotel modelling from a prototype whose
hotel zones simply run hotter. Those 28 cells remain FAIL at their full measured values.

Retail fails a third way, a median narrowly short of a floor under a rule fixed in advance of the
numbers. What the three share is discipline rather than outcome: no reference value was moved and no
scoring rule was changed once it was known which rule would pass. Together they point at reference bands
built for single-use stock lacking the resolving power to judge a channel inside a stacked mixed-use
tower.

Sixteen limitations bound how far these results generalise, and Table 7 gives each one against its
bounding measurement. Three concern what the source data can see at all: hotel guests are outside the
time-use survey frame by construction, so that channel is driven by a provincial tourism series; retail
sees customers only, the survey logging retail workers as at work; and residential intra-household
diversity is partial, 3,499 of 16,367 multi-person households, 21.38 %. Five concern what plausibility is
measured against, and they are why the three failing gates are reported as band-applicability findings:
the office floor is contested and unsourced, the hotel reference is a large-hotel prototype normalized to
a city set this study does not share, retail is validated on shape rather than level, and the residential
channel carries no as-modelled band at all. Three concern internal gains never parameterised by use,
retail zones running the code's office occupant density of 24.97 m2/person against its own retail figure
of 29.97 and equipment power staying a blanket 7.5028 W/m2 across every space type. Two concern the
physical model: the weather file is applied at ground level on a supertall tower, the one limitation with
no bounding measurement, and the hotel domestic-hot-water plant is capacity-pinned on a single object
whose delivered-energy slope against draw volume is -0.98, so only a per-object resize corrects it.

One reproducibility caveat belongs here rather than in that count. This project's own review found that
the residential intensity table published in the authors' prior single-channel study (Iseri and
Hachem-Vermette, under review b) rests on an extraction function carrying two compounding defects, a
demand summary double-counted into an annual energy total and a water-heating guard that zeroes water
energy on SI-unit runs but not on imperial ones; correcting both moved three of the four band verdicts
reported there. The present study is immune for a structural reason: its intensities, reported in Table
5, are read from hourly meter streams and never from the extraction path the defect lived inside.
