# T11. Venue, positioning and the novelty matrix for the shortlisted angles: where each would go, what each must claim, and what reviewers will say

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections A, B, C, E, G, H used. Run in wave 3, after `T02` and `T10`, for the **three angles `T02`
ranked highest and `T10` found feasible**. If those are not yet available, answer for `A2`, `A3` and
`A9`.

## Why we are asking

Our series has a venue pattern: *Energy and Buildings*, *Building Simulation*, *Building and
Environment*, *Journal of Building Performance Simulation*. The fifth paper may fit that pattern or
break it: an agentic or heat-and-health angle reaches communities that do not read those journals.
The choice of angle and the choice of venue decide each other, and both decide the framing, the
structure and how much of the paper is method versus application. Our fourth paper's positioning
round did this exercise for one angle and it shaped the manuscript; this prompt does it for three.

## What we need

### Item 1. Candidate venues, per angle

For each of the three angles, the four best-fitting venues, one Section B row each: scope fit;
whether it has published a paper whose core method resembles the angle (cite it, verified); typical
review turnaround; article-processing charge and waivers; open-access policy; typical length and
structure of a methods-heavy paper there; date checked. Candidates to consider beyond our usual four:
*Applied Energy*, *Sustainable Cities and Society*, *Advanced Engineering Informatics*, *Automation
in Construction*, *Nature Energy*, *Nature Cities*, *Nature Communications*, *Environmental Research
Letters*, *Urban Climate*, *The Lancet Planetary Health* for a heat-health angle, *Scientific Data*
or *Data in Brief* for a dataset deliverable, and a conference route (BuildSys, IBPSA Building
Simulation 2027) as a first release.

### Item 2. The novelty matrix, per angle

For each angle, a matrix whose rows are the closest prior works from `RT02` and whose columns are the
axes on which the angle could claim novelty. Build the axes from the angle itself; we expect them to
include at least: demographically resolved occupancy; district scale with dwelling-level division;
validation against measured data; pre-registered gates; open-weight and open-source; cross-national or
cross-continental transfer; future or extreme weather; released artefacts. Fill it, then state in one
sentence **which combination of cells is genuinely unclaimed**, then attack that sentence with the
strongest argument that the combination is incremental.

### Item 3. The objections and the answers

For each angle, predict the six strongest reviewer objections and for each say what experiment or
number would answer it and whether we can produce it from the assets in master brief section 3. Be
specific about which objections we **cannot** answer; those become the limitations section. We expect,
across the three angles, at least: "a scripted pipeline does this without an agent"; "occupancy does
not change the heat conclusion"; "the null already beats you"; "unvalidated overheating physics";
"the environmental cost of the model is unjustified"; "this is data engineering, not research";
"the districts are not representative".

### Item 4. Series signature

Readers of the first four papers expect a paired frozen-frame EnergyPlus campaign, a pre-registered
gate table and a validated generator. For each angle say whether it keeps that signature, and if not,
whether the loss costs anything with the venues in item 1. Then say which angle a *Building and
Environment* editor would recognise as a continuation and which a *Nature Cities* editor would
recognise as a first paper.

### Item 5. Author-side requirements at the top venue per angle

For the top venue of each angle: structure and length limits; **data and code availability policy,
verbatim**, including how it treats restricted microdata; **AI-use disclosure policy, verbatim**,
noting that a paper whose subject is a language model differs from one written with a language model;
preprint policy; any policy on model or weight availability. Date checked for each.

### Item 6. Framings

For each angle propose three one-sentence framings (methods, transfer or application, policy or
public impact), name the venue each suits, and say which you would choose given that the author's
series is read as building science and two of the fellowship programmes score public impact.

## Named leads

Journal author guidelines and aims-and-scope pages; Scimago and the journals' own turnaround
statistics; the CrossRef API for every citation in the matrices; `RT02` for the prior works.

## Hard constraints specific to this prompt

* Quote author guidelines verbatim for data, code, AI disclosure and preprints, with the date checked.
* Verify every citation used in the matrices through CrossRef.
* Do not recommend a venue on impact factor. Fit and reviewer competence matter more.
* Be blunt in item 2. A novelty claim we cannot defend is worse than a modest one we can.
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** states in its first sentence which angle has the most defensible novelty claim and at
which venue, and in its second which angle carries the most objections we cannot answer.

**Section B** is the venue table from item 1 and the author-requirements table from item 5.

**Section C** is the three novelty matrices with their one-sentence claims and counterarguments.

**Section E** is the objection-and-answer tables from item 3 and the framings from item 6.

**Section G** carries the series-signature judgement from item 4, the unanswerable objections, and
your negative controls.
