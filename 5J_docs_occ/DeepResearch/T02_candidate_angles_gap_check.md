# T02. The ten candidate angles: which are already taken, which are open, and what each would cost us

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
All sections used. Run this **after** wave 1 (`T03` to `T08`, `T13` to `T17`) has returned, because
their landscape tables are its raw material. **The most valuable possible answer is that an angle we
like is already published.** Try hard to find that before concluding it is open.

## Why we are asking

The master brief lists ten candidate angles for the fifth paper, `A1` to `A10`. Each combines assets
we already hold with a direction the field seems to be moving in. Before we spend a year on one, we
need, for each angle, the nearest prior work, what it did and did not do, and whether the combination
we would claim is unclaimed. Our fourth paper's prior-art round did exactly this exercise and it was
the most useful single output of that series.

## What we need

### Item 1. Nearest prior work, per angle

For each of `A1` to `A10`, find the **three closest published or preprint works** and report each as a
Section C row. Closest means: same question, or same data and method, or same deliverable. For each,
the columns of Section C plus one more: **what the authors named as future work, quoted**.

Search each angle under at least three phrasings, and report the phrasings. The building-science and
computer-science communities name the same thing differently, and a search that only uses our
vocabulary will miss the competitor.

### Item 2. The gap and fit table

Fill Section D for all ten angles. For the column **Is it unclaimed?** use exactly `yes`, `partly`
or `no`, and point to the Section C rows that decide it. For `partly`, say which cell of the
combination is taken and which is free.

### Item 3. The strongest objection, per angle

For each angle, write the single strongest sentence a hostile reviewer would open with, and say what
evidence would answer it, and whether that evidence is producible from the assets in master brief
section 3 with the compute in item 5 there. If it is not producible, say so; that angle then carries a
limitation we cannot remove.

### Item 4. Effort and dependency

For each angle: the months of one postdoc's work you estimate, **and the assumption the estimate rests
on**, labelled `INFERENCE`. Name the external dependency that could stall it: a dataset licence, a
partner, an engine feature we do not have, a compute size we do not have.

### Item 5. Angles we did not list

Name up to three angles that the master brief does not list but that the same assets would support
and that item 1 found open. For each, one paragraph and the nearest prior work. Do not exceed three;
we are choosing, not brainstorming.

### Item 6. The ranking, with the rule you used

Rank all angles, ours and yours, on one explicit rule stated before the ranking. The rule must weight
**openness of the gap** above **momentum of the topic**, because a hot topic with a closed gap is a
duplicate paper. Give the ranking as a table. Then say which angle you would drop first and why.

### Item 7. Continuity versus pivot

The four finished papers share one method spine (master brief section 2, last paragraph). For each
angle, say whether it **continues** the spine (a fifth paper readers of the first four will recognise)
or **pivots** away from it, and what each choice costs in a reviewer's eyes: a continuation risks
"incremental", a pivot risks "unproven in this field". Do not resolve the tension; state it per angle.

## Named leads

Scopus, Web of Science, OpenAlex, Semantic Scholar, Google Scholar; arXiv `cs.AI`, `cs.CL`, `cs.LG`,
`cs.CY`, `eess.SY`; the proceedings of IBPSA Building Simulation, BuildSys, CISBAT, SimAUD, eSim and
uSim; IEA EBC Annex 79, 80 and 87 deliverables; the ASHRAE Global Occupant Behavior Database papers;
the Centre for Time Use Research working papers; the UBEM tool papers for UBEM.io, CityBES, URBANopt,
TEASER, CEA, umi and CitySim.

## Hard constraints specific to this prompt

* Every citation verified through CrossRef or arXiv before it appears, with the returned title in
  Section H. On a previous round 9 of 15 DOIs resolved to unrelated papers.
* An angle is `no` (taken) only if a Section C row shows a work that did the combination, not merely a
  component. An angle is `yes` (unclaimed) only after you report the three phrasings you searched.
* Do not pad with generic occupancy or UBEM papers. A row belongs only if it is one of the three
  closest to an angle.
* Do not rank an angle high because the master brief describes it warmly. Section G asks you to check
  this.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first sentence how many of the ten angles are already taken, and names
them.

**Section C** is the landscape table, 30 rows or fewer.

**Section D** is the gap and fit table, ten rows plus yours from item 5.

**Section E** is the ranking from item 6 with the rule stated first, then the continuity table from
item 7.

**Section G** carries the objections we cannot answer, the search phrasings per angle, and your
negative controls: which angle you ranked highest and whether it was also the one the brief described
most warmly; which Section C rows you read in full versus abstract only; whether any row was inferred
from a title alone.
