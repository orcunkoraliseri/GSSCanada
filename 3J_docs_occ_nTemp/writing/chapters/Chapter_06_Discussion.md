# 6 Discussion

Inside one envelope, on one plant, the four populations do not behave as one occupant. They peak at
different hours, hotel at 18.91 h against a midday cluster of 11.90 to 12.37 h, and the whole-building
peak at 14.95 h coincides with none of them. Weekday day-to-night structure differs by an order of
magnitude and in one case by sign, retail 34 to 1, residential 3.9 to 1, hotel inverted. Because the
peaks fall apart, the coincidence factor stays below 1 in every cell, median 0.941. A single-channel
schedule cannot carry a difference between populations.

The architecture makes that observation available. One model trained jointly to output four independent
presence channels, dispatched through a per-space exact-match routing key, carries households, a
workforce, customers and guests each on its own signal, with a decode-time exclusivity projection keeping
them from colliding. The design is additive on the two-channel construction stage, a missing channel
falling back to the untouched code baseline. Bit-identity across stages is not claimed: five of the nine
steps carry no cross-stage comparison, and Table 6 says so.

The office channel fails its energy-use-intensity gate in all 56 cells, and the failure is not the model
under-predicting office demand. The strongest evidence is a control the model never touches: the
uninjected reference implementation, with no occupancy signal, scores 85.45 against the same 100
kWh/m2/yr floor, failing by 15 % before this study contributes a single schedule. Two mechanisms that
would put the model at fault were refuted: measured heating share is about 17 % against the band's
implied 35 to 45 %, the wrong direction, and re-basing on service and mechanical area moves every cell
down. The band's own source states three different floors for itself. Nothing was moved: the floor stays
at 100 and all 56 cells stay FAIL, median 71.02 kWh/m2/yr.

Hotel fails differently, and the geometry of the failure is informative. The 56 measured intensities form
two disjoint clusters tracking the tower prototype: 28 cells at 203.33 to 218.22 kWh/m2/yr, inside the
band, and 28 at 302.86 to 318.42, above the 300 ceiling. The largest gap between consecutive values falls
exactly between them, 84.64 kWh/m2/yr, 70.5 % of the band's width, with the ceiling inside it. A ceiling
anywhere in a gap that wide splits the cells the same way, so the gate cannot distinguish correct hotel
modelling from a prototype whose hotel zones simply run hotter. Those 28 cells remain FAIL.

Retail fails a third way, a median narrowly short of a floor. No reference value was moved and no scoring
rule changed once the outcome was known; together the three point at reference bands built for single-use
stock lacking the resolving power to judge a channel inside a stacked mixed-use tower.

Sixteen limitations bound how far these results generalise, and Table 7 gives each against its bounding
measurement. Three concern what the source data can see: hotel guests are outside the time-use survey
frame by construction, so that channel runs on a provincial tourism series; retail sees customers only,
the survey logging retail workers as at work; and residential intra-household diversity is partial, 3,499
of 16,367 multi-person households, 21.38 %. Five concern what plausibility is measured against, and are
why the failing gates are reported as band-applicability findings: the office floor is contested and
unsourced, the hotel reference is normalized to a city set this study does not share, retail is validated
on shape not level, and the residential channel carries no as-modelled band. The rest concern internal
gains never parameterised by use, survey conventions presented as judgement, and the physical model,
where a ground-level weather file on a supertall tower is the one limitation carrying no bounding
measurement.

One reproducibility caveat belongs here. The residential intensity table in the authors' prior
single-channel study (Iseri and Hachem-Vermette, under review b) rests on an extraction function with two
compounding defects, a demand summary double-counted into an annual energy total and a water-heating
guard that zeroes water energy on SI-unit runs but not imperial ones; correcting both moved three of four
band verdicts. The present study is immune structurally: its intensities, reported in Table 5, are read
from hourly meter streams.
