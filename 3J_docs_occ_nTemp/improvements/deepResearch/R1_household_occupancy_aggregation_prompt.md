# Deep-Research Prompt R1 — How multi-occupant households are aggregated in TUS-driven building energy models

> SCOPE GUARD, READ FIRST. This is a **modelling-convention sourcing** task for two peer-reviewed
> building-simulation papers. The deliverable is **what published time-use-driven occupancy models do
> when a household has more than one member, and what the documented energy consequence of that
> choice is**. It is NOT about occupancy *detection*, sensor fusion, stochastic occupancy model
> families in general, or agent-based mobility simulation. It is not about whether Markov chains beat
> neural networks. If you find yourself writing prose about anything other than **the aggregation
> rule from individual diaries to a zone-level People schedule, and the energy effect of getting it
> wrong**, stop and return to the tables.

---

## Why this matters to the papers

Two papers in one line of work drive EnergyPlus residential zones from Canadian General Social Survey
time-use diaries. Individual respondents are matched to Census agents, agents are grouped into
dwelling units, and each dwelling's People schedule is written.

The rule currently implemented is:

```
People(t) = HHSIZE × 1[ at least one household member is at home at slot t ]
```

That is, the per-slot **maximum** of the members' binary at-home indicators, multiplied by the **full**
household size. A four-person household with one teenager home at 14:00 is modelled as four occupants
in the apartment for that half-hour.

A second, related fact was found in the same audit: in the delivered pool, the maximum is a
byte-level no-op — every co-resident already carries an identical presence vector — so the model
contains no intra-household presence diversity at all.

The first paper is submitted. Its headline finding is a **structural change in the residential load
shape**: midday fill and flattening (Δ midday share +0.37 pp, Δ load factor +0.012) with the evening
peak fixed at ~17:30. Midday is exactly where the aggregation rule has the most room to over-state
occupant gains, because it is when household members are most likely to be *partially* present. The
paper also reports per-household end-use energy calibrated to within ±2.7 % of the national household
energy survey across 48 of 48 dwelling-by-year cells.

So the question is not academic. Either (a) the aggregation rule is the field's normal practice and
the calibration is unaffected, (b) the rule over-states gains and the end-use calibration has
silently absorbed the bias into other parameters, or (c) the rule is materially wrong and the load
shape finding is partly an artefact of it. This prompt exists to find out which.

## Role

You are a building-performance-simulation methodologist. Every claim must cite a named, dated source:
peer-reviewed work, an IEA Annex report, a standard, or a national laboratory technical report. No
inference from what "would make sense". Where the literature is silent, say so — a clean negative is
a result here and is more useful than a plausible reconstruction.

---

## Part A — The deliverable table

For every study you can identify that drives a building energy model from **time-use survey (TUS)
diaries** for **residential** buildings, fill one row:

| Study | Year | TUS source & country | Aggregation rule for multi-occupant dwellings | People count written to the model | Intra-household diversity preserved? | Stated energy effect of the choice | Where stated (section / table) |
|---|---|---|---|---|---|---|---|

The aggregation-rule column should classify into one of these, or name a new one:

1. **Any-present × N** — per-slot maximum over members, multiplied by household size (the rule under audit)
2. **Sum of members** — People(t) = number of members actually present at t
3. **Single-representative** — one diary per dwelling, scaled by a fixed density or by N
4. **Independent per-member schedules** — each occupant gets their own People object or fractional schedule
5. **Household-level diary** — the survey itself samples households, not individuals, so no aggregation is needed
6. Something else — describe it

Studies to check by name, and say explicitly if the paper does not state its rule (that is itself a
finding worth counting):

- **Widén & Wäckelgård (2010)** and the wider Widén line of Swedish TUS-driven models
- **Richardson, Thomson & Infield (2008, 2010)** — the UK TUS active-occupancy model. This line is the
  most likely to have addressed the problem explicitly, since its whole construct is "active
  occupancy" for a household
- **Aerts et al.** (Belgian TUS occupancy sequences)
- **Buttitta & Finn (2020)** and Buttitta et al. — TUS-derived residential load profiles
- **Wilke et al. / Robinson group** — occupant behaviour model chains
- **IEA EBC Annex 66** and **Annex 79** synthesis reports — do either state a recommended practice for
  household aggregation, and if so what?
- **Flett & Kelly**, **McKenna et al.**, **Fischer et al.** — synthetic household occupancy generators
- Any **Canadian** work using the General Social Survey time-use cycles for building modelling
- Any **North American** residential stock model (ResStock, or NREL/PNNL work) that documents how it
  converts occupant counts to schedules

## Part B — The four questions the papers actually need answered

Each in one short paragraph, with citations.

1. **Is "any-present × N" used anywhere in the published literature as the aggregation rule?** If yes,
   name the studies and quote their justification. If no published study uses it, say so plainly —
   that is the single most important finding this prompt can return.

2. **What is the documented magnitude of the difference between "any-present × N" and "sum of present
   members"?** Ideally as an energy or load-shape delta: annual heating/cooling, peak internal gains,
   midday internal-gain intensity. If no study has quantified it directly, give the closest available
   evidence — for example sensitivity studies on occupant density or internal-gain multipliers in
   residential zones — and state clearly that it is an analogue, not a direct measurement.

3. **Is zero intra-household presence diversity a recognised simplification, and what does it cost?**
   Some models deliberately assume co-residents share a presence profile (couples leave and return
   together); others treat members independently. What does the literature say about which regime
   dominates empirically, and what the energy consequence of assuming perfect synchrony is? Note that
   perfect synchrony and "any-present × N" interact: under perfect synchrony the two rules coincide,
   so if synchrony is well supported the aggregation concern largely dissolves.

4. **Does the end-use calibration absorb the bias?** If a model over-states occupant-driven internal
   gains but is then calibrated per-household against a national end-use survey, what does the
   literature say happens — is the bias absorbed into appliance/lighting parameters, does it show up
   as a load-shape distortion that annual calibration cannot see, or both? This is the mechanism the
   first paper's ±2.7 % calibration would have to be defended against.

## Part C — What a defensible statement looks like

Given what you find, draft **two alternative sentences** the papers could use in their methods:

- one for the case where "any-present × N" is standard or immaterial;
- one for the case where it is a simplification that must be declared as a limitation, including how
  its magnitude should be reported.

Say which of the two the evidence supports.

## Output format, follow exactly

1. **Lead with the Part A table fully populated.** Empty cells only where the source genuinely does
   not state the rule, and they must read "not stated" rather than being left blank. Count and report
   how many studies do not state their aggregation rule — that count is itself a finding.
2. Then Part B, four short answers with citations.
3. Then Part C, two draft sentences and a verdict.
4. A **confidence and caveats** section: where sources disagree, where a value is inferred from a
   figure rather than stated, and where European household structure or climate makes a result a poor
   proxy for Canada.
5. A **reference list** with full citations, dates and direct links.

## Hard requirements

- **Distinguish the aggregation rule from the occupancy model.** Two papers can use the same Markov
  occupancy generator and different aggregation rules. It is the aggregation that is being researched.
- **A clean negative is the most valuable outcome here.** If the literature simply does not discuss
  household aggregation — if every paper states its occupancy model in detail and its aggregation rule
  not at all — report that, with the count, and stop. Do not manufacture a consensus.
- **Report findings that weaken the papers plainly.** If the evidence says "any-present × N" over-states
  midday residential gains by a material margin, say so and give the number. The purpose of this task
  is to find out what is true, not to confirm what was implemented.
- Do not re-derive: the occupancy model architecture, the Census linkage method, the SHEU end-use
  benchmarks, or the choice of EnergyPlus. Those are frozen and sourced elsewhere in the project.
- Flag any value borrowed from a different household-structure context (e.g. Nordic single-person
  household prevalence) as a proxy, in the table.
