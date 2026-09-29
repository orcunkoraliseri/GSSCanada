# T38. Gap check and ranking of the data-source forms of angle A14

Paste `00_MASTER_BRIEF.md` first (read its section 9). Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. **Run in wave 7, only after `RT19` to `RT37` are returned and vetted.** Paste the
vetting verdict lines with it (see below).

## Why we are asking

`T19` to `T37` each scouted one source family or one country and each ended with a Section D row
assessing one form of `A14`. This prompt puts those forms side by side, checks each for prior work
once more, and ranks them under one stated rule. It does not choose the paper, and it does not add a
new form.

## Before running (the manager fills this in)

Paste below, as a table, the forms of `A14` that survived vetting, one per row: the form in one
sentence, the `RT` report and row that proposed it, the vetting verdict for that row. If a report
failed its round, its forms are pasted as `route only`.

Vetted table, filled by the manager on 2026-09-19. Every `RT19` to `RT37` report is now vetted.
Forms with vetted support are rows 1 to 4; rows 5 to 12 come from failed rounds and are `route only`.

| # | Form, in one sentence | Report and row | Vetting verdict for that row |
|---|---|---|---|
| 1 | Smart-thermostat presence (ecobee Donate Your Data) as a source for, and check on, time-use occupancy schedules | `RT20` round 2, Section C rows 1 and 2, card 1 | ACCEPTED WITH STRIKES (`VETTING_RT20`). Narrowed: the bare form is done for Canada (Doma, Prajapati, Ouf 2024, DOI 10.1016/j.buildenv.2024.111713) and the US (Jung, Wang, Hong, Jazizadeh 2023, DOI 10.1016/j.buildenv.2023.110628). Open: splits by household and dwelling type, arrival and departure times, matching the homes to the Canadian population. ecobee licence terms unread |
| 2 | The measured bias of time-use diaries on presence at home, and its energy consequence | `RT32` round 2, Section C, Doma row only | FAILED ROUND, Doma row kept (`VETTING_RT32`). The Doma comparison is hourly in aggregate (71 % against 68 %), with no household or dwelling split and no arrival or departure times. The energy consequence is unassessed |
| 3 | Activity-based travel-model populations as the occupancy engine of an urban building energy model | `RT27` round 2, Section C rows 1 to 3 | ACCEPTED WITH STRIKES (`VETTING_RT27`). Narrowed: the coupling is done abroad (a 2026 UrbanSim, POLARIS and CityBES co-simulation; Binder et al. 2020 for Tokyo; Yamaguchi et al. 2023 for Japan). Open: a Canadian version. Toronto model code is GPL-3.0; use of a Toronto or Montreal synthetic population is unknown |
| 4 | Open low-voltage feeder or substation load as a check on occupancy-driven residential load | `RT23` round 2, cards 1, 6, 15 and the LCPR addendum | ACCEPTED WITH STRIKES (`VETTING_RT23`). Open, narrower: open half-hourly feeder data is confirmed only for UK Power Networks (CC BY 4.0, free after registration); Liander is yearly by postcode; Hydro-Québec is system level, plus one hourly file for 3 Montréal substations (CC BY-NC 4.0, 2022 to 2024, no per-home rows, no presence field). Prior art in Section C was struck |
| 5 | Presence inferred from household smart-meter data | `T22` | route only (round 1 failed, `VETTING_RT22`) |
| 6 | A multi-dataset measured-presence benchmark of occupancy generators and standard baselines | `T21`, `T29` | route only (round 1 failed, `VETTING_RT21`, `VETTING_RT29`) |
| 7 | Phone-derived at-home profiles as a calibration target | `T24` | route only (round 1 failed, `VETTING_RT24`) |
| 8 | Day and night population grids as a residential headcount | `T25` | route only (round 1 failed, `VETTING_RT25`) |
| 9 | Regional household travel surveys as a larger, local occupancy source | `T26` | route only (round 1 failed, `VETTING_RT26`) |
| 10 | Frequent non-time-use surveys asking about presence or telework, bridging time-use waves | `RT28` round 2 | route only (FAILED ROUND, `VETTING_RT28`) |
| 11 | Open high-frequency signals of time at home bridging time-use waves | `T33` | route only (round 1 failed, `VETTING_RT33`) |
| 12 | Non-residential and mixed-use presence data | `T30` | route only (round 1 failed, `VETTING_RT30`) |

Licence score (c) in item 2: `RT36` failed its round (`VETTING_RT36`), so score (c) only from a licence
named in the table above (CC BY 4.0, CC BY-NC 4.0, GPL-3.0). Where no licence is named, score (c) as
`licence unread` and give it 0, and say so beside the score.

## What we need

### Item 1. Prior work, once more

For each form: the three nearest works, with identifiers and the CrossRef-returned titles; whether the
form is taken, partly taken or open; the row that decides it.

### Item 2. The ranking

Rank the open and partly open forms under this rule, stated before scoring and applied without
exception: score 0 to 5 on each of (a) openness, (b) data obtainable by a Canadian university within
three months, (c) derived results publishable under the source licence (from `RT36`), (d) fit with the
series method spine (brief section 2: generator, pre-registered gates, paired EnergyPlus campaign),
(e) fit with the fellowship themes (brief section 5). Report each score with the row that justifies
it. Sum with equal weights. Then say whether the order changes if (c) is a hard pass or fail.

### Item 3. Combination with earlier angles

For the top three forms, say whether each is a stand-alone paper or the occupancy module of `A2`,
`A4`, `A8` or `A9`, and cite the rows.

### Item 4. The strongest objection

For each of the top three, the reviewer's strongest objection and whether any asset we hold answers
it.

## Hard constraints specific to this prompt

* No new form may be introduced. A form not in the pasted table is out of scope.
* A form whose only support is a failed-round row cannot rank above a form with vetted support.
* Paste the CrossRef-returned title beside every DOI in every table row. A row without a resolving
  identifier is not admitted.
* Check your ranking against the flattering direction: if the form described most warmly in the brief
  or in the pasted table ranks first, say so and say what evidence other than warmth put it there.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** answers first: the ranked forms, and any that are already taken.

**Section C** is item 1. **Section D** is items 2 and 4. **Section E** is item 3. **Section G** carries
the flattering-direction check and your negative controls.
