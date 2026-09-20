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
5. The tool writes nothing else: no `VETTING_RT<NN>.md`, no edit to this README. If it has file access
   and does so anyway, its note is kept only as an appendix and the manager vets from scratch (added
   2026-09-18, after `RT19` was self-graded).

**Wave 6 in one go.** For an agentic tool with file access, paste `RUN_WAVE6_T20_T37.md` instead. Round 1 ran
`T20` to `T37`; since 2026-09-18 it holds round 2: `T20`, `T23`, `T27`, `T28`, `T32`, `T36`, each with a page
log `RT<NN>_pages.log`. Round-1 reports and notes of those six are kept as `*_round1.md`.

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

  WAVE 4 -- ADJUDICATION (written 2026-09-19, after RT01..RT38 were vetted; run alone)
    T12  contradictions and ranking ....... eleven open questions, one ranking, on a pasted table of checked facts

  --- added 2026-09-18: occupancy data beyond national statistics (angle A14, brief section 9) ---

  WAVE 5 -- the source map, run alone first
    T19  occupancy sources field map ...... which source families were used for occupancy, counted

  WAVE 6 -- one source family or one country each, any order, after T19
    T20  smart thermostats ................ ecobee DYD and peers; measured presence in Canadian homes
    T21  open home sensor datasets ........ registry of homes with measured presence labels
    T22  smart meters ..................... presence inferred from meters; meter sets with surveys
    T23  feeder and grid load ............. open LV feeder and system load as an aggregate check
    T24  phone mobility ................... aggregated at-home signals, hourly profiles by area
    T25  day and night population grids ... ENACT-POP, LandScan; headcount by hour and area
    T26  household travel surveys ......... Montreal OD, TTS, NHTS, NTS; hours away from home
    T27  activity-based travel models ..... MATSim, eqasim, ActivitySim populations as occupancy
    T28  other surveys with presence ...... LFS, RECS, ACS, EWCS; between-wave updates
    T29  simulators and reference schedules the baselines a new source must beat
    T30  non-residential and mixed use .... opening hours, footfall, office and hotel data
    T31  fusion and calibration methods ... combining diaries with measured sources, no circularity
    T32  diaries versus measured presence . how wrong are time-use surveys about being home
    T33  work-from-home in open signals ... continuous signals after 2020 versus two diary waves
    T34  Canadian open data inventory ..... everything Canadian, by custodian
    T35  European data, four districts .... Madrid, Lyon, London, Bologna, like for like
    T36  licences, privacy, release ....... what may be published from each source class
    T37  unconventional sources ........... night light, water, EV, LLM diaries; mostly closed doors

  WAVE 7 -- after RT19..RT37 are vetted
    T38  gap check and ranking of A14 forms  fixed scoring rule; manager pastes the vetted forms first
```

`T10` and `T11` name a fallback trio (`A2`, `A3`, `A9`) for use only if `RT02` is not back. Replace
it with `RT02`'s actual top three before running.

## The prompts

Status values: `written`, `run`, `returned`, `vetted`, `failed`. The manager updates only this column,
in place, dated.

| # | File | Question | What it unblocks | Can it stop an angle? | Status |
|---|---|---|---|---|---|
| **T01** | `T01_hot_topic_field_map.md` | Which clusters have measurable momentum, which calls and agendas name them, which topics are already closed, where our assets are rare | Every later prompt reads against it | Saturation list can | vetted 2026-09-07, with strikes |
| **T02** | `T02_candidate_angles_gap_check.md` | For `A1` to `A10`: nearest three works, unclaimed yes/partly/no, strongest objection, effort, continuity versus pivot, one ranking with its rule | The shortlist | **Yes**, per angle | round 2 returned 2026-09-19, vetted 2026-09-19: FAILED ROUND, do not re-run as it stands (VETTING_RT02; round 1: VETTING_RT02_round1) |
| **T03** | `T03_llm_agents_in_bem_ubem.md` | Has an LLM agent driven a UBEM end to end against ground truth; how many systems reached measured comparison; open-weight tool use on one GPU | `A1` | **Yes** for `A1` | vetted 2026-09-07, with strikes |
| **T04** | `T04_occupant_behaviour_frontier.md` | What the field considers finished after Annex 79; generative and LLM occupants; is time-use occupancy settled or niche; does any occupancy model respond to heat | `A2`, `A3`; the series' own standing | Narrows `A2` | round 2 returned 2026-09-19, vetted 2026-09-19: FAILED ROUND, do not re-run as it stands (VETTING_RT04; round 1: VETTING_RT04_round1) |
| **T05** | `T05_climate_change_heat_and_ubem.md` | Redistributable future and extreme weather for our districts and for Montreal and Toronto; overheating metrics at stock scale and their occupancy assumptions | `A2`, `A4` | Licence could | vetted 2026-09-07 |
| **T06** | `T06_ubem_state_of_the_art.md` | Tool landscape 2024 to 2026; the validation bar; is dwelling-level division with provenance rare; does anyone report cross-platform reproducibility | Every engine-based angle | No | vetted 2026-09-07, with strikes |
| **T07** | `T07_foundation_models_and_multicountry_timeuse.md` | Has anyone claimed a pretrained model for daily activity with measured cross-country transfer; can a Canadian university obtain MTUS and ATUS microdata; harmonisation cost | `A3` | Access could | vetted 2026-09-07 |
| **T08** | `T08_heat_vulnerability_health_equity.md` | Has anyone coupled time-activity occupancy to a thermal model for exposure; does any energy-poverty indicator use time at home; the equity pitfalls we are prone to | `A2`, `A6` | No | round 2 returned 2026-09-19, vetted 2026-09-19: FAILED ROUND, do not re-run as it stands (VETTING_RT08; round 1: VETTING_RT08_round1) |
| **T09** | `T09_fellowship_and_funding_alignment.md` | Programme criteria verbatim; award history as a distribution; angle by programme fit; what counts as evidence at decision dates; programme conflicts | Which angle serves the applications | No, but it can split the choice | round 2 returned 2026-09-19, vetted 2026-09-19: FAILED ROUND, do not re-run as it stands (VETTING_RT09; round 1: VETTING_RT09_round1) |
| **T10** | `T10_data_and_compute_feasibility.md` | For the top three angles: every input as a retrievable artefact, what could ship, compute shape, the one blocker each | Whether the shortlist survives contact with files | **Yes**, per angle | vetted 2026-09-07, with strikes |
| **T11** | `T11_venue_positioning_and_novelty.md` | Venues, novelty matrices, objections, series signature, author-side policies for the top three | Framing and venue | No | vetted 2026-09-07, with strikes |
| **T12** | `T12_contradictions_and_ranking.md` | Adjudicate the open contradictions and rank the surviving angles, from a pasted table of checked facts (`P1` to `P40`) | The decision | No, but it can invalidate earlier answers | returned 2026-09-19, vetted 2026-09-19: ACCEPTED WITH STRIKES, six strikes, do not re-run (VETTING_RT12) |
| **T12, one paste** | `T12_RUN_ALL_IN_ONE.md` | The same run as T12, built from the brief, the template and T12 copied verbatim into one file so the author submits once | The decision | Same as T12 | built 2026-09-19; submit this or the three files, not both |
| **T13** | `T13_why_the_llm_lost_to_the_null.md` | Is "LLM loses to a raked donor pool" a known pattern; explanations; is the null fair; which redesign has measured evidence of beating it; how negative results get published | `A3`; 4J's own write-up | **Yes** for `A3` | vetted 2026-09-07, with strikes |
| **T14** | `T14_scenario_axis_population_weather_stock.md` | How many studies moved climate, population and stock together at district scale; projection sources and licences; attribution methods; what reviewers require of a 2050 projection | `A4` | No | vetted 2026-09-07, with strikes |
| **T15** | `T15_passive_survivability_with_occupants.md` | The survivability literature; habitability standards; density sign reversal; uncertainty without measurement; whether anyone varied presence during an outage | `A9` | No | vetted 2026-09-07, with strikes |
| **T16** | `T16_mixed_use_reference_bands.md` | Does any validated mixed-use reference band exist; has area-weighted composition been tested; is this a paper or an appendix | `A10` | **Yes** for `A10`, expected | vetted 2026-09-07, with strikes |
| **T17** | `T17_llm_reading_records_and_conformal_ubem.md` | LLM extraction from building records with abstention; conformal bounds on a physics-based UBEM; what the registers in six countries contain | `A7` | Data could | round 2 returned 2026-09-19, vetted 2026-09-19: FAILED ROUND, do not re-run as it stands (VETTING_RT17; round 1: VETTING_RT17_round1) |
| **T18** | `T18_privacy_of_synthetic_microdata.md` | Is privacy auditing of generators on microdata standardised; do custodians treat a fine-tuned model as a disclosive output; is a release protocol a paper | Every corpus-trained angle | No | vetted 2026-09-07, with strikes |
| **T19** | `T19_occupancy_sources_field_map.md` | Which non-survey source families were used for building occupancy, counted by year with true-positive share | Every `A14` prompt reads against it | No | failed 2026-09-18 |
| **T20** | `T20_smart_thermostat_presence_data.md` | Can a Canadian researcher obtain thermostat presence data; has it been compared with a time-use survey | `A14` thermostat form | Access could | round 2 returned 2026-09-18, vetted 2026-09-19: ACCEPTED WITH STRIKES (VETTING_RT20; round 1 failed: VETTING_RT20_round1) |
| **T21** | `T21_open_home_sensor_occupancy_datasets.md` | Registry of open datasets with measured residential presence; home-day counts | `A14` benchmark form | Counts could | failed 2026-09-18 (VETTING_RT21) |
| **T22** | `T22_smart_meter_inferred_occupancy.md` | Accuracy of presence inferred from meters against ground truth; meter sets with household surveys | `A14` meter form | Accuracy could | failed 2026-09-18 (VETTING_RT22) |
| **T23** | `T23_network_feeder_and_grid_load_signals.md` | Which operators publish geolocated sub-hourly feeder load; has occupancy been tested against it | `A14` feeder form | No | round 2 returned 2026-09-18, vetted 2026-09-19: ACCEPTED WITH STRIKES (VETTING_RT23) |
| **T24** | `T24_aggregated_mobile_phone_mobility.md` | Which phone-based sources give hourly at-home profiles by area; use in building energy | `A14` mobility form | Resolution could | failed 2026-09-18 (VETTING_RT24) |
| **T25** | `T25_day_night_population_grids.md` | Open day-night grids for our cities; is residential day population separated | `A14` headcount form | Yes, if not separated | failed 2026-09-18 (VETTING_RT25) |
| **T26** | `T26_household_travel_surveys.md` | Access to Montreal and Toronto travel surveys; presence derived from trips | `A14` travel form | Access could | failed 2026-09-18 (VETTING_RT26) |
| **T27** | `T27_activity_based_models_synthetic_populations.md` | Open synthetic populations with daily plans for our cities; any coupled to a UBEM | `A14` activity-model form | Taken could | round 2 returned 2026-09-18, vetted 2026-09-19: ACCEPTED WITH STRIKES (VETTING_RT27) |
| **T28** | `T28_non_time_use_surveys_with_presence.md` | Which frequent public surveys ask about presence or telework, quoted | `A14` between-wave form, `A4` | No | round 2 returned 2026-09-18, vetted 2026-09-19: FAILED ROUND, do not re-run in Gemini (VETTING_RT28) |
| **T29** | `T29_open_occupancy_simulators_and_reference_schedules.md` | Standard schedules and open simulators; what each is built on; any validated against measured presence | Baselines for every `A14` form | No | failed 2026-09-18 (VETTING_RT29) |
| **T30** | `T30_non_residential_mixed_use_occupancy_data.md` | Open office, retail, hotel presence data; opening hours at scale | `A14` with `A10`, 3J channels | No | failed 2026-09-18 (VETTING_RT30) |
| **T31** | `T31_data_fusion_and_calibration_methods.md` | Fusion methods with precedent on diary-type plus measured data; keeping a held-out check | Method for every `A14` form | No | vetted 2026-09-18, with strikes |
| **T32** | `T32_time_use_versus_measured_presence.md` | Measured evidence on how diaries err about presence at home, and the energy consequence | `A14` diary-bias form | Yes, if already done | round 2 returned 2026-09-18, vetted 2026-09-19: FAILED ROUND, Doma row kept (VETTING_RT32) |
| **T33** | `T33_work_from_home_shift_in_open_signals.md` | Continuous open signals of time at home after 2020 and their agreement with diaries | `A14` with `A4` | No | failed 2026-09-18 (VETTING_RT33) |
| **T34** | `T34_canadian_open_data_inventory_for_occupancy.md` | Every Canadian source bearing on presence or residential load, by custodian | Canadian arm, `A8` | No | failed 2026-09-18 (VETTING_RT34) |
| **T35** | `T35_european_open_data_for_the_four_districts.md` | Local open sources for Madrid, Lyon, London, Bologna, like for like | European arm | No | failed 2026-09-18 (VETTING_RT35) |
| **T36** | `T36_legal_licence_privacy_of_non_survey_sources.md` | Licences, TCPS 2, Law 25, GDPR: what may be released per source class | Every `A14` form | **Yes**, per source class | round 2 returned 2026-09-18, vetted 2026-09-19: FAILED ROUND, do not re-run in Gemini (VETTING_RT36) |
| **T37** | `T37_emerging_and_unconventional_occupancy_sources.md` | Night light, water, EV, Wi-Fi, LLM-written diaries: real, closed or hype | Closes doors early | Yes, expected | failed 2026-09-18 (VETTING_RT37) |
| **T38** | `T38_source_angles_gap_check_and_ranking.md` | Prior work and one fixed-rule ranking of the vetted `A14` forms | The `A14` shortlist | **Yes**, per form | round 2 returned 2026-09-19, vetted 2026-09-19: FAILED ROUND, do not re-run as it stands; forms unchanged (VETTING_RT38; round 1 void: VETTING_RT38_round1) |

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
