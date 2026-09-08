# T01. Field map: what is actually hot, 2024 to 2026, at the intersection of LLMs, occupancy modelling, UBEM and climate change

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections A, B, C, E, F, G, H used. Run this **first**, alone. Every other prompt in the series is read
against the map this one returns.

## Why we are asking

We are choosing the subject of our fifth paper. We have a working pipeline that turns national time-use
microdata into occupancy for EnergyPlus, an open-weight LLM fine-tuned on harmonised European time-use
diaries, and an open-source UBEM engine with validated US cells and four European districts. We do not
know which of the possible directions is a rising topic with open questions, which is a crowded topic
whose open questions were closed in 2025, and which is a topic only we care about.

We want the map before we choose the road. **We are not asking you to pick our paper.** We are asking
what the field is publishing, funding and calling for, with evidence we can re-run.

## What we need

### Item 1. Topic clusters with measurable momentum

Identify the topic clusters that sit at the intersection of at least two of the four fields (large
language models, occupant behaviour and occupancy modelling, urban building energy modelling, climate
change and heat). For each cluster give one Section B row with:

1. A name and a one-sentence definition.
2. **Publication counts by year, 2021 to 2026**, from a query you actually ran on OpenAlex, Scopus,
   Web of Science or Semantic Scholar. Quote the exact query string and the date run, so we can re-run
   it. If you cannot run a query, write `NOT COUNTED` rather than an estimate.
3. Three anchor papers, each with a CrossRef-verified DOI, read at least at abstract level.
4. Whether the cluster is **emerging** (counts rising, few methods settled), **maturing** (methods
   settled, application papers multiplying) or **saturated** (reviews and benchmarks dominate, novelty
   now incremental). Say what evidence made you place it there.
5. The strongest open question the cluster's own authors name as future work, quoted.

We expect the clusters to include at least: LLM agents for building simulation workflows; LLMs as
occupant or household simulators; generative models for occupancy and activity schedules; UBEM under
future climate and heat; urban overheating and indoor heat exposure at stock scale; passive
survivability and resilience of neighbourhoods; occupant-centric demand flexibility and
electrification; UBEM calibration and trust with smart-meter data; synthetic populations for energy
and mobility; language models extracting building attributes from records. Add what we have missed
and drop what the counts do not support.

### Item 2. Special issues, calls for papers, and conference tracks open now

List every special issue or thematic call in *Energy and Buildings*, *Building and Environment*,
*Applied Energy*, *Building Simulation*, *Journal of Building Performance Simulation*, *Sustainable
Cities and Society*, *Advanced Engineering Informatics*, *Automation in Construction*, *Nature Energy*,
*Nature Cities*, *Scientific Data*, and the IBPSA, ASHRAE, BuildSys, CISBAT, SimAUD and eSim conference
cycles that is **open on the day you check** and touches any cluster from item 1. Give title, venue,
submission deadline, guest editors, the URL you opened, and the date checked. A closed call is
`CLOSED`, not omitted, if it closed after 2025-06-01, because it still shows where editors think the
field is going.

### Item 3. Research agendas and roadmaps

What do the field's own agenda documents say the open problems are? We mean: IEA EBC Annex 79 final
deliverables and whatever annex succeeds it on occupant behaviour; Annex 80 on resilient cooling and
any annex on overheating; the IBPSA position papers; the ASHRAE Multidisciplinary Task Group outputs on
occupant behaviour; the IPCC AR6 WGIII buildings chapter research gaps; the EU Mission on Climate
Neutral and Smart Cities research agenda; the US DOE BTO multi-year plan; any 2025 or 2026 review
titled as a roadmap for AI in building performance. For each: the document, the year, the three gaps
it names, and whether any of our four fields is named explicitly.

### Item 4. Funding signals

Which programme calls, 2025 and 2026, fund work at these intersections? Horizon Europe Cluster 5 and
the Built4People partnership; Marie Sklodowska-Curie Actions; ERC panels PE8 and SH; NSERC Alliance and
Discovery; NRCan and CMHC research programmes; Mitacs; US DOE BENEFIT and ARPA-E; UKRI; Swedish Energy
Agency and Formas; Swiss SNSF and Innosuisse. For each hit: call title, deadline, budget line, the
sentence in the call text that names the intersection, URL opened, date checked. This feeds `T09`.

### Item 5. Saturation warnings

Name explicitly the topics that a reviewer in 2026 would regard as **done**: where a benchmark exists,
a review consolidated the methods, or a widely cited paper closed the obvious question. For each, name
the closing work. This is the most valuable item for us, because our previous rounds tended to
recommend the topic the prompt led with, and we want the list of doors that are already shut.

### Item 6. Where our assets create asymmetry

Given only what the master brief says we hold (section 3 there), name the clusters where those assets
are rare in the literature. Say for each what the literature typically lacks that we have: harmonised
multi-country diaries, a fine-tuned open-weight generator with a documented negative result, a
district-scale engine with dwelling-level division, a validation discipline with pre-registered gates.
Do not flatter. If a cluster is full of groups with better assets, say so.

## Named leads

OpenAlex API (`https://api.openalex.org/works?search=...`) for counts, because its queries are
reproducible without a subscription; Scopus and Web of Science if reachable; IEA EBC annex pages;
IBPSA publications database; the journal special-issue pages; the EU Funding and Tenders portal; the
NSERC and NRCan programme pages; arXiv `cs.AI`, `cs.CL`, `cs.CY`, `eess.SY`, `physics.soc-ph`.

## Hard constraints specific to this prompt

* Every count carries the query string and the date. A count without a query is `NOT COUNTED`.
* Every deadline, call and special issue carries the URL you opened and the date checked. Calls change
  monthly and we will re-open every one.
* Do not name a cluster hot because it sounds hot. Counts, calls or agenda documents, or it is
  `ASSERTED, NOT MEASURED`.
* Do not recommend a paper subject. Section E says what the map changes about how we should choose,
  not what we should choose.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first sentence how many clusters you found with measurable momentum, and
in its second sentence which of the four fields is the most crowded.

**Section B** is the cluster table from item 1, then the calls table from item 2, then the funding
table from item 4.

**Section C** is the anchor-paper landscape table.

**Section E** says what this changes about how we should choose a subject.

**Section F** lists every roadmap, call text and agenda document we should download.

**Section G** carries the saturation list from item 5, the asymmetry assessment from item 6, and your
negative controls: which counts you could not run, which calls you named from memory rather than
opened, and whether any cluster in item 1 was placed as emerging because the prompt listed it.
