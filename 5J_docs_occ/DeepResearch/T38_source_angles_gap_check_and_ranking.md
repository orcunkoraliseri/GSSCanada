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

Fallback list, used **only** if the vetted table is not ready, and to be replaced before running:

| Form | Proposed in |
|---|---|
| Thermostat presence as validation for time-use occupancy | `T20` |
| Multi-dataset measured-presence benchmark of occupancy generators and standard baselines | `T21`, `T29` |
| Phone-derived at-home profiles as a calibration target | `T24` |
| Regional travel surveys as a larger, local occupancy source | `T26` |
| Activity-based travel populations as the occupancy engine of a UBEM | `T27` |
| The measured diary bias on presence and its energy consequence | `T32` |
| Open high-frequency signals bridging time-use waves | `T33` |

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
