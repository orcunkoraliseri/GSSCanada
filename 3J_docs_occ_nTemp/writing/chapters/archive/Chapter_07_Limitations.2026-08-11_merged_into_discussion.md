# 7 Limitations

Sixteen limitations bound the interpretation of these results. Fifteen carry a bounding measurement;
the sixteenth carries none and is marked as unquantified rather than given an invented figure. Table 7
lists all sixteen against their measurements.

Three concern what the source data can see at all. Hotel guests are outside the General Social Survey
frame by construction, so the hotel channel is driven by a provincial tourism series rather than by
time-use data, and the survey observes none of hotel occupancy; the paper's own framing is therefore
three of four channels time-use-driven and one series-driven. Retail sees customers only, because the
survey logs retail workers as at work rather than as shopping, so no retail staff presence enters the
signal and no retail plug load is modulated by it. Residential intra-household presence diversity is
partial rather than complete, and an earlier and stronger internal claim that it was exactly zero is
falsified by direct measurement: 3,499 of 16,367 multi-person households, 21.38 %, carry at least one
slot value outside zero, one half and one. A surviving defect behind that number is that one pipeline
stage computes a household maximum which a later stage never reads, the aggregation actually applied
downstream being the mean.

Five concern what plausibility is being measured against. The office band's floor is contested and
unsourced, which makes its gate a band-applicability finding rather than a model defect: the uninjected
control scores 85.45 kWh/m2/yr against a floor of 100, two candidate mechanisms were tested and refuted,
and the source document gives three different floors for itself. Chapter 6 develops this in full, and
the value is not moved to make the gate pass. The hotel band is archetype- and city-mismatched, and the
mismatch is stated rather than absorbed into a tolerance: this study's tower is NECB-2017 Montreal and
Calgary, while the reference is the DOE/PNNL Large Hotel at ASHRAE 90.1-2019, first-party values 284.44
kWh/m2/yr for climate zone 6A and 299.28 for zone 7. A vintage-matched alternative sits 1.0 % from the
current ceiling, so it is the archetype and the city set, not the vintage, that remain at issue. A
"stacked channel" explanation once offered for the hotel channel's low values, that a mid-tower channel
carries little roof, ground or facade load and should read low, was tested and refuted in all 56 cells
and is cited nowhere in this paper: hotel is the least thermally exposed of the three banded channels
and sits closest to its floor rather than furthest from it, and geometry varies only between the two
prototypes, so the exposure ratio the explanation needs takes two values across the campaign rather
than 56. The retail channel is validated on shape rather than on level, because no population-denominated
in-store presence reference exists at time-of-day resolution in the American, harmonized European or
United Kingdom time-use surveys checked for this study; its gate rule is median-in-band rather than a
56-of-56 count, because the measured spread is smaller than the quantity's own re-run uncertainty, and
its presence-rate gate was separately demoted to informational status because the two available
references disagree in direction rather than only in magnitude. The residential channel carries no
as-modelled band at all: the SHEU-2019 high-rise figure, 130.6 kWh/m2/yr over a range of 113.9 to 147.2,
is carried as context and never used as a pass criterion, because a residential channel inside a
mixed-use tower is not the housing stock that survey sampled.

Three concern internal gains that were never parameterised by use. Retail zones run the code's office
occupant density, 24.97 m2/person, rather than the code's own retail figure of 29.97, so retail is
modelled roughly 20 % over-crowded relative to the code's own reference. Equipment power density is a
single blanket value of 7.5028 W/m2 applied to every space type in both prototypes while lighting is
differentiated per space type, making occupant density and equipment power density the two internal-gain
fields never parameterised in this pipeline. The retail occupancy peak of 0.95 has no independent source,
and the code's own retail schedule was never loaded into the injected model: that schedule peaks at 0.80
at 16:00 with no midday dip, while the tower instead carries the code's office schedule, peaking at 0.90
with a lunch-hour dip to 0.50, with a further 0.95 multiplier applied on top. Retail therefore runs
approximately 18.75 % hot at peak, and on the wrong-shaped curve.

Three concern method conventions that are judgement rather than derivation, and are presented as such.
The minimum adjustment-cell pool size of fifteen respondents is an analyst judgement call; no numeric
convention for a minimum of this kind was located in the literature checked, the anchor previously cited
for it in fact gives five as that source's own study design, and the corresponding gate is measured to
be non-monotonic in the pool size, which rules it out as a principled selection criterion. Household
aggregation is the mean, and this is a decision rather than an inheritance, because the three
construction stages behind this project do not agree with one another; this pipeline's choice was
verified against its own code rather than against another stage's documentation. The retail episode-time
share declines across survey cycles, at 2.00 %, 2.14 %, 1.66 % and 1.50 %, an approximately 25 % decline
that comparable American, European and United Kingdom series independently confirm as internationally
normal; an earlier internal claim that the share was stable was a documentation defect rather than a
measurement.

Two concern the physical model. The weather file is applied at ground level on a supertall tower, and
this is the one limitation here with no bounding measurement: no altitudinal temperature or wind-speed
gradient is represented over a tower of this height, and establishing one would require either a vertical
weather profile or an instrumented tall building, neither of which this study has. It is listed with an
explicit "not quantified" rather than a plausible-sounding invented bound. The hotel domestic-hot-water
plant is capacity-pinned on a single object, and a global correction does not correct it: that heater's
delivered-energy slope against draw volume is -0.98 in both tested arms, so delivered energy is almost
completely insensitive to how much water is drawn, and raising a single global sizing factor to six
drove every other heater's slope to zero and moved the pinned heater's share of hotel hot-water demand
from 26.7 % to 65.4 %, a reweighting that alone reproduces the resulting elasticity. The instrument that
addresses the defect is a per-object resize, not a building-wide multiplier.

One further point belongs here as a reproducibility caveat rather than as a seventeenth limitation. The
residential energy-use-intensity table published in the authors' prior single-channel study (Iseri and
Hachem-Vermette, under review b) was found, during this project's own review, to have been computed by a
shared extraction function carrying two compounding defects: a demand-summary table double-counted into
an annual energy total as though it were an energy rather than a power quantity, and a water-heating
guard that correctly zeroes water energy on SI-unit runs but fails to recognise imperial units, so that
on imperial-unit runs a water volume is summed into the reported intensity as if it were electricity.
Every run in that campaign carried exactly one of the two defects, decided by which unit system the run
used, and correcting both moved three of the four reported band verdicts there. The present study is
immune to that defect for a structural reason rather than an incidental one: its intensities, reported
in Table 5, are read from hourly EnergyPlus meter streams and never from the tabular extraction function
the defect lived inside. The two pipelines share a lineage and, at points, shared code, but not this
extraction path, and that difference, rather than a targeted fix, is what protects the values reported
here.
