# T16. Reference energy bands for buildings that stack several uses: does any validated benchmark exist, and how would one be built

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections A, B, C, E, F, G, H used. Run in wave 1, after `T01`. This is the narrowest prompt in the
series and a short, negative answer is acceptable.

## Why we are asking

Our third paper drove a mixed-use tall building (residential, office, retail, hotel) with four
occupancy channels and scored the result against reference EUI bands borrowed from single-use stock.
Three of the four channel gates failed, one of them in the control run before any occupancy signal
was injected, which says the bands, not the model, may be wrong for stacked uses. The paper names as
future work reference bands **constructed for, and validated against, buildings that stack more than
one use**. Angle `A10` asks whether that is a paper or a footnote.

## What we need

### Item 1. Existing benchmarks for mixed-use buildings

Which measured-energy benchmarks, disclosure datasets or rating schemes report mixed-use buildings as
a class, and how do they treat the mix: ENERGY STAR Portfolio Manager, CBECS, NYC LL84 and other US
disclosure laws, the UK Display Energy Certificates and CIBSE TM46, the EU EPC schemes, the Canadian
ENERGY STAR Portfolio Manager adaptation and provincial disclosure, Chinese and Japanese benchmarks
for high-rise mixed-use. For each: how mixed use is defined, how area is apportioned between uses,
what the reported EUI distribution is, sample size, and licence. Section F rows.

### Item 2. Published methods for a mixed-use reference

Any 2010 to 2026 work that constructs an expected EUI for a mixed-use building from its use mix:
area-weighted composition of single-use benchmarks, regression on use shares, simulation-based
prototypes (PNNL tall and supertall prototypes included), or measured cohorts of mixed-use towers.
For each: method, data, validation against measured mixed-use buildings, and the error reported.
Report specifically whether anyone has **tested whether area-weighted composition of single-use
bands predicts measured mixed-use EUI**, because that test decides whether a new band is needed.

### Item 3. Interaction effects

What is known about energy interactions between stacked uses that an area-weighted band would miss:
shared cores and plant, heat transfer between differently conditioned uses, diversity of coincident
peaks across uses, shared domestic hot water and elevators. Cite measured or simulated evidence with
magnitude.

### Item 4. Data for a Canadian or European mixed-use cohort

Where could measured whole-building energy for mixed-use towers be obtained for Montreal, Toronto,
Calgary or our four European districts: disclosure programmes, utility partnerships, published case
studies. What aggregation and what licence. `NOT FOUND` is likely for Canada; say so with the search.

### Item 5. Is this a paper?

State in one paragraph whether the literature leaves room for a paper whose contribution is a
validated mixed-use reference band, or whether the honest outcome is a methods note or an appendix in
the third paper's revision. Give the venue that would take each form.

## Named leads

ENERGY STAR Portfolio Manager technical references; CBECS microdata documentation; NYC LL84 and
Seattle, Chicago and Boston disclosure datasets; CIBSE TM46 and DEC documentation; PNNL prototype
building reports; *Energy and Buildings*, *Building and Environment*, *Energy Policy*, *Building
Research and Information*; the Canadian Energy and Water Reporting and Benchmarking programmes in
Ontario and British Columbia.

## Hard constraints specific to this prompt

* Every EUI distribution carries its sample size, year and normalisation (site or source, weather
  normalised or not).
* Do not recompute or reinterpret our third paper's gates.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first sentence whether any validated mixed-use reference band exists, and
in its second whether area-weighted composition has been tested against measured mixed-use buildings.

**Section C** is the methods table from item 2.

**Section F** is the benchmark table from item 1 and the data table from item 4.

**Section E** is items 3 and 5.

**Section G** carries your negative controls.
