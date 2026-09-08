# T-series deep research prompts (5J: choosing the fifth paper)

Prompts for **external** deep research (Gemini Antigravity). Written in-repo, run outside it. The
returned reports come back into **this same directory**, beside the prompt that produced them.

Same convention as `4J_docs_occ/DeepResearchPrompts/` (prefix `L`) and
`3J_docs_occ_nTemp/deepResearch_Resources/` (prefix `V`), with the prefix changed to `T` so the three
series never collide in a search.

Written 2026-09-07 from four read-only scans of our own documents, kept in `_scan/`:
`scan_gsscanada_progress.md`, `scan_openubem_capabilities.md`, `scan_openubem_explanation.md`,
`scan_fellowship_applications.md`. The master brief was written from them; re-read them before
changing the brief.

## What this series is for

The fourth paper is about to be written up. This series asks the literature, the funders and the
journals what is hot, what is closed, and where the assets we already hold (harmonised time-use
corpora, a fine-tuned open-weight generator with a documented negative result, the OpenUBEM engine,
a pre-registered validation discipline) are rare. It does **not** ask the tool to pick the paper. The
choice is the author's, made after the reports are vetted and `T12` adjudicates their contradictions.

The candidate angles `A1` to `A10` are defined once, in `00_MASTER_BRIEF.md` section 4, and used by
every prompt. Add an angle there, not in a prompt.

## How to run one

1. Paste `00_MASTER_BRIEF.md` into the external tool.
2. Paste the `T<NN>_*.md` prompt after it.
3. The tool answers using the schema in `_RESPONSE_TEMPLATE.md` (Sections A to H).
4. Save the answer here as `RT<NN>_<topic>.md`, same topic slug as the prompt.

**One prompt per session.** The master brief tells the assistant to answer only what follows it, and
the response template is per prompt.

## Run order

```
  WAVE 0 -- the map, run alone and read before anything else
    T01  hot-topic field map .............. counts, calls, agendas, saturation, asymmetry

  WAVE 1 -- one frontier each, any order, all independent of one another
    T03  LLM agents in BEM and UBEM ....... A1: what exists, how rigorous, open-weight feasibility
    T04  occupant-behaviour frontier ...... after Annex 79; generative occupants; heat response
    T05  climate, heat and UBEM ........... A2 A4: future weather artefacts, overheating at scale
    T06  UBEM state of the art ............ where the engine stands; dwelling division; validation bar
    T07  foundation models, corpora ....... A3: MTUS ATUS HETUS access; "foundation model" claims
    T08  heat, health, equity ............. A2 A6: does resolving who is home change the answer
    T13  why the LLM lost to the null ..... A3: is the pattern known; what beats a raked donor pool
    T14  scenario axis .................... A4: population + weather + stock, combined, to 2050
    T15  passive survivability ............ A9: standards, uncertainty, occupants during outages
    T16  mixed-use reference bands ........ A10: narrow; a short negative answer is fine
    T17  records with abstention, conformal  A7: LLM extraction, prediction sets, coverage on a UBEM
    T18  privacy of synthetic microdata ... every angle that trains on HETUS or GSS inherits this

  WAVE 2 -- the gap, the funders, the files (run after wave 1 is back and vetted)
    T02  candidate angles gap check ....... taken / partly / open for A1..A10; ranking; continuity
    T09  fellowship and funding alignment . programme texts verbatim; award history; angle fit
    T10  data and compute feasibility ..... for T02's top three: what opens today, what could ship

  WAVE 3 -- positioning (run after T02 and T10)
    T11  venue, positioning, novelty ...... three venues, three matrices, the objections

  WAVE 4 -- ADJUDICATION (write it after RT01..RT18 are vetted; not yet written)
    T12  contradictions and ranking ....... reserved number; written from the vetted reports
```

`T10` and `T11` name a fallback trio (`A2`, `A3`, `A9`) for use only if `RT02` is not back. Replace
it with `RT02`'s actual top three before running.

## The prompts

Status values: `written`, `run`, `returned`, `vetted`, `failed`. The manager updates only this column,
in place, dated.

| # | File | Question | What it unblocks | Can it stop an angle? | Status |
|---|---|---|---|---|---|
| **T01** | `T01_hot_topic_field_map.md` | Which clusters have measurable momentum, which calls and agendas name them, which topics are already closed, where our assets are rare | Every later prompt reads against it | Saturation list can | vetted 2026-09-07, with strikes |
| **T02** | `T02_candidate_angles_gap_check.md` | For `A1` to `A10`: nearest three works, unclaimed yes/partly/no, strongest objection, effort, continuity versus pivot, one ranking with its rule | The shortlist | **Yes**, per angle | failed 2026-09-07 (VETTING_RT02) |
| **T03** | `T03_llm_agents_in_bem_ubem.md` | Has an LLM agent driven a UBEM end to end against ground truth; how many systems reached measured comparison; open-weight tool use on one GPU | `A1` | **Yes** for `A1` | vetted 2026-09-07, with strikes |
| **T04** | `T04_occupant_behaviour_frontier.md` | What the field considers finished after Annex 79; generative and LLM occupants; is time-use occupancy settled or niche; does any occupancy model respond to heat | `A2`, `A3`; the series' own standing | Narrows `A2` | failed 2026-09-07 (VETTING_RT04) |
| **T05** | `T05_climate_change_heat_and_ubem.md` | Redistributable future and extreme weather for our districts and for Montreal and Toronto; overheating metrics at stock scale and their occupancy assumptions | `A2`, `A4` | Licence could | vetted 2026-09-07 |
| **T06** | `T06_ubem_state_of_the_art.md` | Tool landscape 2024 to 2026; the validation bar; is dwelling-level division with provenance rare; does anyone report cross-platform reproducibility | Every engine-based angle | No | vetted 2026-09-07, with strikes |
| **T07** | `T07_foundation_models_and_multicountry_timeuse.md` | Has anyone claimed a pretrained model for daily activity with measured cross-country transfer; can a Canadian university obtain MTUS and ATUS microdata; harmonisation cost | `A3` | Access could | vetted 2026-09-07 |
| **T08** | `T08_heat_vulnerability_health_equity.md` | Has anyone coupled time-activity occupancy to a thermal model for exposure; does any energy-poverty indicator use time at home; the equity pitfalls we are prone to | `A2`, `A6` | No | failed 2026-09-07 (VETTING_RT08) |
| **T09** | `T09_fellowship_and_funding_alignment.md` | Programme criteria verbatim; award history as a distribution; angle by programme fit; what counts as evidence at decision dates; programme conflicts | Which angle serves the applications | No, but it can split the choice | failed 2026-09-07 (VETTING_RT09) |
| **T10** | `T10_data_and_compute_feasibility.md` | For the top three angles: every input as a retrievable artefact, what could ship, compute shape, the one blocker each | Whether the shortlist survives contact with files | **Yes**, per angle | vetted 2026-09-07, with strikes |
| **T11** | `T11_venue_positioning_and_novelty.md` | Venues, novelty matrices, objections, series signature, author-side policies for the top three | Framing and venue | No | vetted 2026-09-07, with strikes |
| **T12** | reserved | Adjudicate the contradictions among `RT01` to `RT18` and rank the angles | The decision | No, but it can invalidate earlier answers | not written |
| **T13** | `T13_why_the_llm_lost_to_the_null.md` | Is "LLM loses to a raked donor pool" a known pattern; explanations; is the null fair; which redesign has measured evidence of beating it; how negative results get published | `A3`; 4J's own write-up | **Yes** for `A3` | vetted 2026-09-07, with strikes |
| **T14** | `T14_scenario_axis_population_weather_stock.md` | How many studies moved climate, population and stock together at district scale; projection sources and licences; attribution methods; what reviewers require of a 2050 projection | `A4` | No | vetted 2026-09-07, with strikes |
| **T15** | `T15_passive_survivability_with_occupants.md` | The survivability literature; habitability standards; density sign reversal; uncertainty without measurement; whether anyone varied presence during an outage | `A9` | No | vetted 2026-09-07, with strikes |
| **T16** | `T16_mixed_use_reference_bands.md` | Does any validated mixed-use reference band exist; has area-weighted composition been tested; is this a paper or an appendix | `A10` | **Yes** for `A10`, expected | vetted 2026-09-07, with strikes |
| **T17** | `T17_llm_reading_records_and_conformal_ubem.md` | LLM extraction from building records with abstention; conformal bounds on a physics-based UBEM; what the registers in six countries contain | `A7` | Data could | failed 2026-09-07 (VETTING_RT17) |
| **T18** | `T18_privacy_of_synthetic_microdata.md` | Is privacy auditing of generators on microdata standardised; do custodians treat a fine-tuned model as a disclosive output; is a release protocol a paper | Every corpus-trained angle | No | vetted 2026-09-07, with strikes |

## Rules that hold for every prompt in this series

* The master brief is pasted first, every time. Its section 4 defines the angles and its section 3
  states the negative result of 4J plainly. **No prompt asks how to make 4J's gate pass**; `T13`
  makes proposing that a failed round.
* Only public programme information is used for the fellowships. **No prompt names or asks for
  individuals** connected to the applications, and `T09`, `T15` and `T17` forbid it explicitly.
* Every count carries its query and date; every call, deadline, licence and version carries the URL
  opened and the date checked; every DOI is verified through CrossRef and the returned title shown.
* `NOT FOUND` is a successful answer. Several prompts (`T04` item 4, `T05` item 2.3, `T08` items 2.2
  and 3.2, `T13` item 4, `T15` item 5.2, `T16`) are written so that a negative is the expected
  outcome and say so.
* No em dashes and no en dashes in any returned text.

## Vetting a returned report, BEFORE any value enters a planning document

This project has run more than thirty rounds of external deep research across three papers. **Every
early round contained fabricated or laundered content, and every one was caught by cheap offline
checking.** Run these before reading a single value into a plan.

1. **Check its claims about our own work first.** The tool cannot see our results, our engine or our
   applications. Anything it says about them is either quoted from the brief or invented.
2. **A report that agrees with something you supplied has told you nothing.** The diagnostic value is
   entirely in what we did not supply: the counts, the closed doors, the taken angles.
3. **Check metadata columns, not only value columns.** Dates checked, URLs opened, "read: full or
   abstract". A copied table gives itself away in its provenance.
4. **Make it obey an identity it cannot fake.** A DOI returns a title or it does not. A call page has a
   deadline or it does not. An OpenAlex query re-run returns the same count or it does not.
5. **Version and date rot is this series' failure mode.** Calls, special issues, model versions and
   licences change monthly. Re-check anything older than about three months.
6. **Expect the answer to inherit the prompt's framing.** `T02` asks in its own negative controls
   whether the highest-ranked angle was also the one the brief described most warmly. Trust `T02`
   least if it ranks `A1` or `A2` first with enthusiasm and no taken-angle finding.
7. **Every recommendation moving in the flattering direction is a signal.** If a report finds every
   angle open, every programme a strong fit, every dataset downloadable and every venue receptive,
   treat it as a failed round and re-run with the negative controls tightened.

**When a round fails, salvage the route, not the table.** A query string we can re-run, a call URL we
can open, a register we can download are worth more than sixty rows we have to falsify.

Vetting notes go in `VETTING_RT<NN>.md` in this directory, one per report or per pair, as in the 4J
series.

## What comes after the reports

Nothing in this directory decides the paper. After `RT01` to `RT18` are vetted, `T12` is written from
their contradictions and run; then the author chooses an angle; then a `5J_docs_occ` plan document is
opened for it. The manager prompt for those sessions is `PROMPTS/New_ideas_Manager_Prompt.md` at the
repository root.
