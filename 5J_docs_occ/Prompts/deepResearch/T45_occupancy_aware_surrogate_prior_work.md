# T45. Has anyone trained an EnergyPlus surrogate that takes an occupancy sequence and is scored on the occupancy effect

Paste `00_MASTER_BRIEF_5J.md` first, then `_RESPONSE_TEMPLATE.md`, then this prompt, in one fresh
session. **Run it alone: do not run any other prompt in this session, before or after.** Written
2026-09-28. Your files are `RT45_occupancy_aware_surrogate_prior_work.md` and `RT45_pages.log` (one
line per page, record or file you opened: URL, what it was, full / abstract / title, date). Save both in
this folder.

## Why we are asking

The paper design in brief section 2 is fixed. Before any claim is written we need to know which parts
of it the published record already covers. An earlier outside search judged this design "open", but it
left two on-point coupling papers from its own log out of the answer and gave wrong author names for a
third. So this round asks narrower questions, and checks itself against papers we hold in full.

## The parts of the claim to test

* **P1. Occupancy sequence as surrogate input.** A learned surrogate or metamodel of a building energy
  simulation (EnergyPlus, TRNSYS, IDA ICE, DOE-2, Modelica or similar) whose inputs include an
  occupancy, presence, activity or schedule **time series**, not only a scalar (density, hours per day)
  or a fixed schedule name.
* **P2. Scored on paired differences.** A surrogate scored on the **difference** between two
  simulations of the same building (occupancy change, retrofit change, control change), not only on
  each simulation's load. Retrofit-savings or counterfactual scoring counts; say which.
* **P3. A blind or ablated control.** A surrogate study that retrains or tests with one input shuffled,
  permuted, removed or held constant, to show that the model uses that input.
* **P4. Time-use diaries feeding a learned energy model.** Diaries (HETUS, MTUS, ATUS, a national
  time-use survey) used as the input to a trained model of building energy, as opposed to a model that
  only generates occupancy.
* **P5. Hourly residential surrogates at stock or district scale, 2019 to today.** Any trained model
  that replaces building simulation for many dwellings at hourly resolution, whatever its inputs.

## What we need

### Item 1. The three works we already know (controls and one retrieval)

For each, give: title from the registry record, authors from the registry record, venue, year, and in
at most four sentences what the work did, what its learned part is (if any), what goes in and what
comes out, and how it was scored. Say what you read (full, abstract, title).

* **K1.** `10.26868/25222708.2015.2655`
* **K2.** `10.1007/978-981-97-8309-0_1`
* **K3.** `10.2172/1817464`. We could not open this report (its host did not respond from our side).
  We also need: a **direct URL to a file** of the full report (OSTI full text, the laboratory's own
  publication page, a later journal or conference version by the same authors, or a repository copy),
  and the report's own words (quoted, with page) on **what the surrogate's inputs are**, and whether
  occupancy or schedules are among them. If you cannot open the full text, write `NOT FOUND` for the
  quotation, and say what you did open.

K1 and K2 are controls: we hold both in full and will compare your description sentence by sentence.

### Item 2. Prior work per part

For each of P1 to P5, the nearest works (up to eight per part), one Section C row each: authors from
the registry record, year, venue, DOI or arXiv ID; which part it is near; the simulation engine; the
surrogate's inputs, **quoted or paraphrased from the paper with page or section**; the outputs and
their time step; how it was scored; whether it scored differences between runs; whether it had a blind
or ablated control; what it did not do; `Read:` full, abstract, or `TITLE ONLY`.

### Item 3. Verdict per part

One Section D row per part: done, partly done, or open as far as searched, naming the Section C row
that decides it. Then one sentence on the whole claim of brief section 4: which part is best supported
as new, and which part is already covered. A verdict of "open" lists its queries with their log lines:
"these queries found nothing", never "no such work exists".

## Named leads

OpenAlex, Semantic Scholar, CrossRef, arXiv, OSTI, IBPSA proceedings (Building Simulation, SimBuild,
eSim, BSO), ASHRAE conference papers, ACM BuildSys and e-Energy, Tackling Climate Change with Machine
Learning workshops. Journals: Energy and Buildings, Building and Environment, Applied Energy, Energy and
AI, Journal of Building Performance Simulation, Building Simulation, Sustainable Cities and Society,
Renewable and Sustainable Energy Reviews (review articles on building energy surrogates or metamodels
are a good starting point: follow their reference lists and say which review you used). Query terms,
alone and combined: "surrogate model", "metamodel", "emulator", "reduced-order", "EnergyPlus",
"building energy simulation", "occupancy", "occupant behaviour", "schedule", "time use", "activity",
"stochastic occupancy", "hourly load", "residential", "urban building energy", "deep learning",
"transformer", "LSTM", "graph neural network", "ablation", "counterfactual", "retrofit savings",
"difference", "paired".

## Hard constraints specific to this prompt

* **Positive controls.** K1 and K2 must be described correctly (item 1). A report that misstates what
  either did, what goes in, or whether it trains a model fails the round, whatever else it contains.
* **Search strength.** Your logged searches must also surface, on their own, at least one published
  review of building energy surrogate or metamodel methods. If they do not, say so in Section G; the
  "open" verdicts are then too weak to use.
* **Negative control.** If all five parts come back open, say in the first sentence of Section A that
  your searches were probably too weak, because at least P2 (retrofit-savings scoring) and P5 are
  expected to have prior work.
* Before writing `TITLE ONLY`, try at least one open copy (publisher abstract page, arXiv, Semantic
  Scholar or OpenAlex abstract) and log each try.
* No accuracy or speed-up number unless quoted with its page (brief section 5).
* No em dashes and no en dashes anywhere in the output.

## Deliverable

**Section A** first, in at most eight sentences: which parts of the claim are already done, by which
works, and whether the claim of brief section 4 still stands as written. **Section B**: one row per
fact you want us to cite. **Section C**: items 1 and 2 (K1 to K3 first, then P1 to P5). **Section D**:
item 3, each verdict marked `[INFERENCE]`. **Section E**: what should change in the framing, tied to C
rows. **Section F**: the K3 file link and any code or dataset a Section C work released (landing page
opened, access condition quoted). **Section G**: the control results, queries that found nothing with
their log lines, works you could not open, and the four standard questions of the template.
**Section H**: full references.
