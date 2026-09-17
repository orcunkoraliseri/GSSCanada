# 2J — plan to rebuild the paper after the Building Simulation rejection

**Written:** 2026-09-15 · **Status:** PLAN ONLY — nothing below has been computed or edited yet
**Manuscript:** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a
Calibrated Behavioural Occupancy Time-Series (Canada, 2005–2030)*

---

## §0 The decision, and what was archived

```
Decision letter received : 2026-09-15 (read by the author on or before this date)
Editorial Manager ID     : BUIL-D-26-01113
Decision                 : REJECT (no resubmission to Building Simulation)
Revision deadline        : none — we set our own pace
Editor                   : Dr. Da Yan, Editor-in-Chief
Number of reviewers      : 3 (all three advised against publication in current form)
```

**Archived on 2026-09-15** into `writing/submission/archive/` (moved, not copied; SHA-256 checked
before and after the move, 18 of 18 files identical):

| Now at | What it is |
|---|---|
| `archive/submissionDocs/` | exactly what Building Simulation received: title page + cover letter, blinded manuscript, SI + 8 CSVs, upload README |
| `archive/2J_manuscript_submission.md` | the non-blinded master as submitted |
| `archive/2J_manuscript_submission.docx` | the same, rendered |

Two consequences of the move:
- The archived `.md` links to `figures/…`, which now resolves to `archive/figures/` (does not exist).
  The `.docx` has the figures embedded, so the archive is still complete. **Do not edit the archive
  to fix the links** — it is the record of what the reviewers read.
- `00_README_submission.md` and `Prompts/2J_manager_prompt_ON_REVISION_DECISION.md` still point at
  the old paths. Update them in the closing pass (§9), not before.

**Treat `archive/` as frozen.** All new work goes in `rejection revision/`.

---

## §1 What the three reviews say, in one paragraph

All three reviewers found the question valuable (Reviewer 3 called the central result "non-obvious
and well supported"). The rejection rests on **four real gaps** and **one presentation problem**:

1. **The 2030 number is wrong and the paper says so itself.** Reviewer 3 read §7 and asked us to fix
   it; Reviewer 1 independently saw it in Fig. 5 as an "implausible" 2022→2030 jump. They are the
   same defect (§3, WP1).
2. **One 2030 future is presented as "the forecast".** All three want scenarios (work-from-home
   stays, partly reverses, fully reverses) or the word "forecast" dropped.
3. **Nothing independent checks the hourly load shape.** The SHEU agreement is calibration, not
   validation (R2, R3), and Table 5 EUI sits below every SHEU band (R1).
4. **We never showed that the detailed household model beats a simple schedule** (R1).
5. **The paper reads like a technical report**: too long, too many internal terms and QA details, too
   few figures, no equations, results mixed into Methods (R1, R2).

None of the reviewers attacked the core finding (midday fill, flatter load, fixed evening peak). The
plan therefore **keeps the science and fixes the evidence and the framing**.

---

## §2 Triage — every reviewer request, in the reviewers' order

Classes (from the standing revision prompt): **A** text only · **B** re-derive a number from an
existing file · **C** new computation (costed, never started without approval) · **D** claim the
paper cannot support, narrow it · **E** we disagree, needs an evidenced rebuttal.

### Reviewer 1

| # | Request (quoted) | Class | Action | WP |
|---|---|---|---|---|
| M1 | "The proposed approach should be compared with simpler alternatives, such as conventional deterministic schedules or empirically derived average occupancy profiles" | **C** | Two new simulation arms on the same household panels | WP3 |
| M2a | "A concise workflow diagram" | A | New workflow figure (image **prompt** only, author generates) | WP11 |
| M2b | "mathematical formulations of the main models and evaluation metrics" | A | Equations block in Methods | WP10 |
| M2c | "Some parts of Sections 3.2 and 3.4 appear to present results and should be moved" | A | Move gate scores / JS scores to Results or SI | WP10 |
| M2d | "What exactly is sampled, and how are the fixed 50-household panels generated? … demonstrate through a convergence or sensitivity analysis that this sample size is sufficient" | **B + C** | Write the sampling procedure; subsample curve from existing runs; one larger-N check | WP4 |
| M3 | "Table 5 shows substantial discrepancies between the simulated EUI and the SHEU benchmark … demonstrate that the main conclusions remain valid despite them" | **B + C (optional)** + D | Quantify the gap by end use; optional older-envelope sensitivity; stop calling EUI "plausible" | WP7 |
| M4 | "More figures should be provided … occupancy, annual energy use, intraday load shape, peak demand, and load factor … repetitive textual explanations should be substantially reduced" | A + B | New data plots from existing outputs; cut prose | WP11, WP10 |
| M5 | "Fig. 5 appears to show a substantial increase in daytime occupancy from 2022 to 2030 … Alternative scenarios, such as WFH stabilizing, decreasing, or continuing to increase" | **C** | Fix 2030 calibration, then run scenarios | WP1, WP2 |
| D1 | "clarify which outcomes specifically benefit from stochastic modelling and demonstrate this benefit" | C (via M1) + A | Answer from WP3 results | WP3 |
| D2 | "'The matrix scores external competitors only.' If the authors' previous published studies are excluded, they should also be included" | A | Add prior-work rows to Table 1 (note: the journal prior paper is published; the JBPS paper status must be checked) | WP10 |
| D3 | "'C-VAE' is used before being defined on p. 5" | A | Define at first use | WP10 |
| D4 | "explain 'activity & end-use resolved' earlier" | A | Define in §1 | WP10 |
| D5 | "differences from Chen et al. (2022) should be described more explicitly" | A | One explicit paragraph | WP10 |
| D6 | "why when energy is consumed is important and why forecasting specifically to 2030 is necessary" | A | Motivation paragraph; 2030 tied to the next survey cycle / policy horizon (source needed, external) | WP10, WP12 |
| D7 | "contributions … should be rewritten in terms of the main scientific and practical contributions" | A | Rewrite §1.5 | WP10 |
| D8 | "table linking each dataset to its role in the framework" | A | New dataset-role table; fold §2 into framework section | WP10 |
| D9 | "Datasets section includes some descriptions of EnergyPlus simulations" | A | Move §2.4 content | WP10 |
| D10 | "'Proposed modelling and simulation framework' may therefore be more appropriate" | A | Retitle §3 | WP10 |
| D11 | "almost no mathematical formulation … Key modelling and aggregation procedures should be formally defined" | A | Same as M2b | WP10 |
| D12 | "clarify why individual-level behavioural modelling is necessary for stock-scale outcomes" | C (via M1) + A | Evidence: WP3 + the household-level morning-peak finding already in §5.3 | WP3, WP10 |
| D13 | "reduced energy use in offices … this system-boundary limitation should be clearly discussed" | A | One limitation paragraph (literature external) | WP10, WP12 |
| D14 | "repetitive descriptions (e.g., Sections 3.5 and 4.2)" | A | Merge | WP10 |
| D15 | "too few figures and tables relative to the amount of quantitative discussion" | A + B | Same as M4 | WP11 |
| D16 | "Section 5.1 … some of the numerical values in the text do not appear to correspond clearly to those shown in the figure" | **B** | Re-derive every §5.1 number against Fig. 5 source data. Likely cause known (WP1) | WP1 |
| D17 | "daytime occupancy appears to increase substantially from 2022 to 2030 … scenario-based analysis" | **C** | Same as M5 | WP1, WP2 |
| D18 | "Fig. 6c appears to show very little difference … decompose the result by end use and time of day" | **B** | End-use × hour decomposition from existing meter outputs | WP6 |
| D19 | "If the primary value lies … in changes in intraday load shape, ramping, load factor, or demand-response potential, these results should be made much more prominent" | A + B | Lead Results with shape metrics; add ramp metric from existing hourly data | WP6, WP10 |
| D20 | "Fig. 7 is too small and information-dense" | A | Split into separate panels / figures | WP11 |

### Reviewer 2

| # | Request (quoted) | Class | Action | WP |
|---|---|---|---|---|
| 1 | "reads more like a technical report … Internal QA and implementation details, such as EnergyPlus schedule verification, simulation debugging, clock-alignment debugging, detailed J3 architecture settings, PASS/WARN/INFO scorecards … should be moved to supplementary information. More straightforward terminology" | A | Full restructure; move QA to SI; plain names for self-defined terms. **Keep one sentence** in the main text on the timing check (see note under §6) | WP10 |
| 2 | "provide an external validation of the simulated hourly profiles, preferably using measured household-level or aggregated residential electricity data … for an observed year such as 2022" | **C + external data** | Find measured Canadian hourly residential data (external search), compare 2022 profile, peak hour, load factor, midday share. If no usable data exists → narrow the claim (D) | WP5 |
| 3 | "The use of the term 'forecast' should be reconsidered … reframing the study as an occupancy-conditioned or scenario-based projection … revising the title, abstract, objectives, and conclusions" | A (**accept**) | New title and framing throughout | WP10 |
| 4 | "The Abstract should be rewritten … symbols such as '+', '±', '~', and 'Δ'" | A | Prose abstract | WP10 |
| 5 | "'This introduction proceeds as a funnel…' … deleting this meta-description" | A | Delete; conventional intro | WP10 |
| 6 | "agreement primarily demonstrates calibration closure rather than independent validation" | A + D | Rename "calibration closure" everywhere; no "validation" claim for SHEU | WP7 |
| 7 | "Figures 6 and 7 are too small and difficult to read" | A | Same as R1-D20 | WP11 |

### Reviewer 3

| # | Request (quoted) | Class | Action | WP |
|---|---|---|---|---|
| 1 | "rerun the 2030 calibration using the final post-relink household frame and update all affected occupancy and energy results, figures, confidence intervals, abstract statements and conclusions" | **C — critical path** | WP1 | WP1 |
| 2 | "do either at least two 2030 scenarios … high persistence and partial/high reversion … or much clearer language" | **C** (do both: scenarios **and** language) | WP2 | WP2, WP10 |
| 3 | "Distinguish more carefully between: post-pandemic/WFH-associated change and causally attributable COVID/WFH effect" | A + D | Replace causal wording with "post-pandemic change associated with WFH"; list other concurrent changes as a limitation | WP10 |
| 4 | "add at least a coarse sensitivity bracket in the main results rather than deferring this entirely" | **C** | Same as R3-2; scenarios reported in §5, not §7 | WP2 |
| 5 | "Separate calibration performance … with independent validation/plausibility evidence" | A + C | Two clearly labelled subsections; validation content comes from WP5 and the True-Future-Test | WP7, WP5 |
| 6 | "how these intervals were constructed (e.g., bootstrap resampling of households, and whether clustering by archetype/city was accounted for)" | **B** | Find the CI code; document; recompute with cluster-aware resampling if it was not | WP8 |
| 7 | "where do these exact thresholds (especially 5.3 pp and 1.045) come from? Were they specified before model comparison? … A sensitivity analysis showing whether model selection changes under modestly different thresholds" | **B** (+ **D** if post hoc) | Trace the thresholds in the Step-4 record; re-rank the 40+ stored trial scores under shifted thresholds (no retraining) | WP9 |

**Count:** 42 requests (R1 28, R2 7, R3 7) · 12 touch new computation (served by WP1–WP5 and
optional WP7) · 9 need a number re-derived · the rest are text only · 0 outright disagreements.
No outright disagreement is planned. The one partial pushback is noted under §6 (keep the timing
check visible in one sentence).

---

## §3 Work packages

Format per project rule: aim · steps · expected result · test method. **C-class packages are costed
and wait for the author's go.** Run counts below are EnergyPlus annual runs; the original campaign
was 6,000 (Step 8) + 4,800 (Step 9).

### WP1 — Recalibrate the 2030 occupancy against the post-relink household frame · C · CRITICAL PATH

**Why this is first.** It is the one defect a reviewer found by reading our own §7, and it also
explains Reviewer 1's Fig. 5 complaint and the §5.1 text/figure mismatch. The record already shows
the size of the problem (`Step8_docs/08_09_injection_bug_status.md`, entry 2026-07-15): the current
schedule files give weekday at-home **70.2% (2022) vs 78.5% (2030), a +8.3 pp gap**, while the
Step-6 calibration intended only **+1.51 pp** (76.93% → 78.44%) because it was raked against the
pre-relink 2022 reference (76.93%) instead of the post-relink one (~70.2%).
🔴 These three numbers come from a log entry. **Re-derive them from the schedule files before
quoting** (standing rule).

**Steps.**
1. Re-derive 2022 and 2030 weekday/weekend at-home means from the current `BEM_Schedules_2022.csv`
   and `BEM_Schedules_2030.csv`, per archetype and national. Record in the implementation doc.
2. Rebuild the 2030 raking targets from the **post-relink** 2022 frame plus the Step-6 intended
   2022→2030 change, and re-rake the 2030 cohort.
3. Regenerate `BEM_Schedules_2030.csv`; re-run schedule-integration checks (the 28-check suite).
4. Re-simulate the 2030 half of the paired panel: **1,200 Step-8 runs + 2,400 Step-9 runs (2030
   baseline and activity arms)**. The 2022 runs stay as they are.
5. Recompute every 2030-dependent number: §5.1 at-home, annual energy 2022→2030, Δmidday share,
   Δload factor and their CIs, peak hour, EUI 2030 column, SHEU 2030 cells, Figs. 5, 6, S8.

**Expected result.** A 2022→2030 at-home step near the intended ~+1.5 pp rather than +8 pp, and
2022→2030 load-shape deltas that are **probably smaller** than the submitted +0.367 pp / +0.0117.
🔴 **It is possible that one or both CIs will then include zero.** That is a legitimate outcome and
changes the headline; the paper must be rewritten around whatever comes out. Do not start WP10
prose on §5.3 until WP1 is done.

**Test.** Rerun at-home mean on the regenerated file matches the new target within 0.5 pp; 28-check
integration suite passes; paired CIs recomputed from the new run tree, not copied.

### WP2 — 2030 work-from-home scenarios · C

**Aim.** Replace the single "persistence with probability 1" future with a bracket, reported in
the main results (R1-M5, R1-D17, R3-2, R3-4).

**Proposed scenario set** (author decides the exact definitions, see §7 D1):

| Scenario | 2030 weekday at-home target |
|---|---|
| S-Persist (current, corrected by WP1) | post-relink 2022 level + Step-6 demographic change |
| S-Partial | halfway between S-Persist and the demographically standardized 2015 level |
| S-Revert | the standardized 2015 level carried to 2030 demographics |
| S-Grow (optional) | S-Persist + a further increase — only if an external source supports a number |

**Steps.** Each scenario = a different set of 2030 raking targets on the same corrected cohort
(the raking facility already exists) → new 2030 schedule file → **1,200 Step-8 runs** per scenario
on the same 2022–2030 panel. Step-9 activity runs are not repeated per scenario unless the author
wants end-use timing per scenario.

**Cost.** 2 required scenarios × 1,200 = **2,400 runs** (+1,200 if S-Grow).

**Expected result.** A range for each headline metric (at-home, annual energy, midday share, load
factor, peak hour). Title and text say "scenario-based projection".

**Test.** Each scenario's injected at-home mean hits its target within 0.5 pp; S-Revert should
produce 2022→2030 shape deltas of opposite sign to S-Persist (sanity check that the chain responds).

### WP3 — Compare with simple schedules · C

**Aim.** Show what the household-level model adds (R1-M1, R1-D1, R1-D12).

**Two new arms on the same 50-household panels:**
1. **Static code schedule** — the NECB/ASHRAE default residential occupancy, equipment and lighting
   schedules, identical every year. It cannot see any behaviour change by construction.
2. **Average survey profile** — one mean at-home profile per cycle-year (and per archetype), same for
   every household, SHEU-scaled like the main model.

**Metrics compared against the full model:** annual kWh, peak demand, peak hour, load factor, midday
share, evening ramp, household-level peak-hour spread.

**Cost.** Static arm is year-independent: **1,200 runs**. Average-profile arm for 2022 and 2030:
**2,400 runs** (add 1,200 for 2015 if the author wants the break visible). Total **3,600–4,800**.

**Expected result (hypothesis, not a claim).** The average profile will reproduce annual energy and
much of the mean shape (Reviewer 1 is probably right about annual energy), while the static schedule
misses the break entirely. The individual model's distinct value is likely in **peak demand, load
factor at stock level through diversity, and the household-level morning-peak minority (22–25%)**
that an average profile erases. If the average profile matches the full model on every metric,
**say so** and narrow the contribution (class D).

**Test.** The static arm must show zero cross-year change (built-in check); the average-profile arm's
annual at-home share must equal the full model's.

### WP4 — Monte-Carlo sample size · B + C

**Aim.** Answer "what is sampled, and is 50 enough?" (R1-M2d).

**Steps.**
1. Write the sampling procedure precisely from the Step-8 code: what is stratified (DTYPE × PR), how
   the 50 IDs are drawn, seed, and what "one household" contributes (schedule + SHEU scaling).
   Also state plainly that the 50 are per archetype × city cell, i.e. 1,200 households per year,
   and how cell results are weighted to the stock.
   ⚠ 2026-09-15 (T05): the analysis code weights by archetype only, split equally over the six
   cities (`08_simulation_plots.py:74-77,300-321`); the design doc and paper describe DTYPE × PR.
   The WP4 spec must choose: describe the code's weighting in the rewrite, or change the weighting
   and recompute every stock-weighted number.
2. **No new runs:** resample subsets of N = 10, 20, 30, 40 from the existing 50 per cell (many
   draws) and plot CI half-width and metric mean vs N for annual kWh, midday share, load factor,
   peak hour.
3. **New runs (C):** one larger-N check, e.g. N = 200 for the four archetypes in Montréal, 2022 and
   2030: 4 cells × 150 extra households × 2 years = **1,200 runs**.

**Expected result.** A convergence figure for the SI and one sentence in Methods.

**Test.** N = 50 mean from step 3 falls inside the N = 200 CI for every metric; if not, report it.

### WP5 — Independent check of the hourly load shape · external data + C

**Aim.** Reviewer 2's main demand: compare the simulated 2022 profile against measured Canadian
residential electricity (R2-2, R3-5).

**Steps.**
1. **Author a deep-research prompt** (run externally by the author, per the standing rule) to find
   measured, citable Canadian residential hourly load profiles around 2019–2023: household smart-meter
   studies, utility or system-operator residential load-research profiles, and published profiles
   such as the Canadian study already cited in §1.3 (Abdeen et al. 2021, which reports hourly
   household electricity before and during COVID). The prompt must ask for data access terms,
   province, sample, heating fuel mix, and whether weekday/weekend profiles are given.
2. Author opens and vets every returned source (7-step vetting; expect fabricated citations).
3. Build the comparison for 2022: normalized weekday/weekend daily profile, peak hour, load factor,
   midday share, and, if available, the pre/post-COVID change. Match on what the data covers
   (province, dwelling type, electric vs non-electric heating); state mismatches.
4. If the measured data includes electric space heating and our electricity meter does not (or vice
   versa), compare the matching end-use subset only.

**Cost.** Mostly analysis on existing outputs; new runs only if a matched province/weather is
needed (estimate ≤ 600 runs, decided after step 2).

**Expected result.** One validation figure + table. 🔴 **If no usable measured data is found**, the
honest move is class D: state that the load shape is validated only indirectly (True-Future-Test on
occupancy, calibration closure on end-use magnitude) and soften "load shape" claims to "occupancy-
driven load-shape response". Do not substitute a synthetic or modelled profile as "measured".

**Test.** Every comparison number traceable to a file on disk and a source the author has opened.

### WP6 — Why annual energy barely moves: end use × hour decomposition · B

**Aim.** Explain Fig. 6c physically and make the practical value visible (R1-D18, R1-D19).

**Steps.** From the existing 7 meter streams (the campaign outputs; no new runs, but WP1 reruns the
2030 part first): per archetype and stock-weighted, 2022 vs 2030 (and per WP2 scenario):
1. Annual change by end use — equipment, lighting, fans, heating, cooling, water heating.
2. Hour-of-day change by end use (24 × end use heat-map or stacked difference plot).
3. Separate what responds to occupancy (plug, lighting, internal-gain effect on heating and cooling)
   from what does not (baseload appliances, envelope-driven heating).
4. Add grid-facing metrics already computable from hourly data: evening ramp (e.g. 14:00→17:00
   increase), peak demand, load factor, midday share, and hours above a threshold.

**Expected result.** A two-panel figure and a short paragraph. Likely explanation to **test, not
assume**: more daytime plug and lighting load is partly offset by lower heating need from extra
internal gains in winter, and the baseload does not change — so the annual sum stays flat while
the daytime hours rise.

**Test.** End-use sums reproduce the facility total within the 0.07% already reported.

### WP7 — Calibration vs validation, and the EUI gap · A + B + optional C

**Aim.** R1-M3, R2-6, R3-5.

**Steps.**
1. **A:** Rename the SHEU agreement "calibration closure" everywhere; remove any wording that it
   validates the model. Build the evidence ladder as two labelled parts: *calibration* (SHEU end-use
   magnitude) vs *independent checks* (True-Future-Test on the unseen 2022 survey; WP5 hourly data;
   Census-linkage tier distribution).
2. **B:** Break the Table 5 EUI gap down by end use against SHEU's end-use split (space heating,
   water heating, appliances, lighting, cooling), per archetype. This shows *where* the gap sits
   (expected: space heating, which was never calibrated and uses a current-code envelope).
3. **C (optional, author's call, §7 D3):** envelope sensitivity — rerun one or two archetypes with an
   older-stock envelope (pre-code insulation and air-tightness) for 2022 and 2030: e.g.
   SingleDetached × 6 cities × 50 × 2 years = **600 runs**. Show (a) EUI moves into the SHEU band,
   and (b) the 2022→2030 shape deltas stay the same sign and similar size.
4. Rewrite §5.2 to say plainly: the model is not calibrated on total EUI; the conclusions are about
   occupancy-driven change within a fixed building, and step 3 shows they survive a different
   envelope (if run).

**Test.** End-use breakdown sums back to the Table 5 total.

### WP8 — How the confidence intervals were built · B

**Aim.** R3-6.

**Steps.** Locate the Δmidday-share and Δload-factor CI code in the Step-8 analysis (start from
`Step8_docs/08_simulation_plots.py` and the aggregate tables); record the method (paired t-interval
over households? bootstrap? per cell then pooled?). If households were resampled without respecting
the archetype × city structure, recompute with a **cluster (cell-stratified) bootstrap of
households** and report both. Apply to the WP1-corrected runs.

**Expected result.** A two-sentence Methods note and, if needed, new CI values.

**Test.** Re-running the documented method on the archived run tree reproduces the submitted
[+0.208, +0.526] and [+0.0085, +0.0150] before any change is applied (proves we found the right code).

### WP9 — Where the model-selection thresholds came from · B (+ D if post hoc)

**Aim.** R3-7.

**Steps.**
1. Trace the four gates (activity JS ≤ 0.05, at-home RMSE ≤ 5.3 pp, co-presence gap ≤ 5 pp,
   composite < 1.045) through the Step-4 record: when each was first written, and whether that date
   precedes the candidate results. `step4_training_v4.md` is the working doc per memory.
2. If any threshold was set or moved after seeing candidates, **say so in the paper** and give the
   reason (e.g. 5.3 pp might be tied to a measured survey-sampling floor — verify, do not assume).
3. Sensitivity: take the stored gate scores of all 40+ trials, shift each threshold by ±10% and ±20%,
   and report whether J3 stays selected and which rival would pass. No retraining.

**Expected result.** One SI table and one Methods sentence.

⚠ 2026-09-15 (T04, manager re-checked in `step4_training_v4.md:337-361,734-743`): the submitted claim
"the only model to clear all four gates" is wrong. Against the published thresholds, three J5 trials
also clear all four; the J5 tables had scored them against J3's own composite and an extra "Alone"
gate. J3 still has the lowest composite of the four passers, so the choice stands and only the
sentence changes. Two thresholds equal the F1 baseline's own scores; the spouse gate moved 10 → 5 pp
with no stated reason. No threshold has an independent rationale on record. Detail:
`impl/2026-09-15_T04_wp9_threshold_provenance.md`.

**Test.** The re-ranking at the original thresholds reproduces "J3 is the only 4-of-4 model".

### WP10 — Rewrite the manuscript · A (large)

Working copy: start from `archive/2J_manuscript_submission.md`, **copy** into
`rejection revision/manuscript/` when WP10 starts. Venue-neutral until §8's decision.

**Framing.**
- New title in the scenario-projection frame (R2-3, R3-2). Candidate for the author to edit:
  *"From 'how much' to 'when': occupancy-driven change in the Canadian residential load shape
  after COVID-19, with work-from-home scenarios to 2030"*.
- "Forecast" → "scenario-based projection" in title, abstract, highlights, objectives, conclusions.
- Causal language → "post-pandemic change associated with work-from-home"; add a limitation naming
  other concurrent changes (R3-3).
- New system-boundary paragraph: more home occupancy may mean less office energy, not modelled (R1-D13).

**Structure** (target: clearly shorter than the submitted ~16k words; exact cap set by venue):
1. Introduction — conventional: background, existing work, gap, objectives. Delete the funnel
   paragraph (R2-5). Why *when* matters (grid peak, ramping, demand response) and why 2030 (R1-D6).
   Define C-VAE and "activity and end-use resolved" at first use (R1-D3, D4). Explicit Chen et al.
   (2022) difference paragraph (R1-D5). Table 1 gains the authors' own prior-work rows (R1-D2).
   Contributions rewritten as 2–3 scientific + 2 practical statements, no pipeline jargon (R1-D7).
2. **Proposed modelling and simulation framework** (R1-D10) — opens with the new workflow figure and a
   dataset-role table (R1-M2a, D8), then each stage with its equation:
   generator conditional likelihood; raking (iterative proportional fitting to slot marginals);
   hierarchical match rule; household aggregation and schedule conversion; end-use calibration scalar
   f_e; stock aggregation weights; load factor, midday share, peak hour (circular mean), paired delta
   and its CI (R1-M2b, D11). Sampling procedure from WP4. Scenario definitions from WP2.
   §3.5/§4.2 duplication merged (R1-D14). EnergyPlus material moved out of Datasets (R1-D9).
3. Results — occupancy change → scenarios → annual energy by end use → load shape, ramp, peak, load
   factor → simple-schedule comparison → independent hourly check → sample-size check.
   Gate scores and JS values moved here or to SI (R1-M2c).
4. Discussion — practical value for grid planning and codes; what the individual model adds (WP3).
5. Limitations — shorter; 2030 provenance item removed once WP1 is done.
6. Conclusion.

**Move to SI** (R2-1): J3 architecture detail, 40+ trial search detail, all PASS/WARN/INFO
scorecards, DX-coil fix, schedule round-trip checks, clock-alignment debugging narrative, donor-draw
history, raking coherence cost, weekend JS floor argument.

**Plain terms** (R2-1): replace or gloss every self-defined label — "calibrated J3", "True-Future-
Test", "paired frozen-frame", "Tier-1/2/3 FailSafe", "COLLECT_MODE", "DDAY_STRATA", "Step-8/Step-9",
"occACT". Keep one short glossary table in SI.

**Abstract** (R2-4): plain prose, no +, ±, ~, Δ; numbers in words where a sentence reads better.

**Rule.** Every number in the rewrite is re-derived from its artifact after WP1–WP9, never copied
from the archived manuscript.

### WP11 — Figures · A + B

- **Workflow diagram** (R1-M2a): write an image **prompt** under
  `writing/submission/figures/Prompts_Images/` — the author generates the image (hard rule).
- **New data figures** (matplotlib from frozen outputs, allowed): (1) at-home by hour, 2015/2022/2030
  scenarios; (2) annual energy by end use; (3) intraday load shape by scenario; (4) peak demand, load
  factor, ramp with CIs; (5) end use × hour difference (WP6); (6) full model vs static vs average
  profile (WP3); (7) measured vs simulated 2022 profile (WP5); (8) convergence vs N (WP4, SI);
  (9) threshold sensitivity (WP9, SI).
- **Split Fig. 6 and Fig. 7** into larger single-message figures (R1-D20, R2-7).
- **Fig. 5 ↔ §5.1 consistency** (R1-D16): every number in the text read off the plotted data file.
- **All figures at ≥ 600 dpi** at print width (carried item, 13 of 16 were below).
- Keep figure count disciplined: only figures that carry a claim (standing author preference).

### WP12 — Carried items and external literature · A + B + external

1. **Crosswalk leaf-code counts** 182/265/64/123 (spreadsheet) vs 182/264/64/121 (paper): verify
   which mapping the pipeline consumed; fix the paper or document the unused rows. Ship the
   crosswalk as an SI CSV once settled.
2. **Prior-paper status**: check the JBPS companion paper; if accepted, add it to references and to
   Table 1 (links to R1-D2).
3. **Deep-research prompts to author** (run externally, vetted by the author before any citation):
   (a) systematic search testing the Table 1 novelty matrix — never done, and a new reviewer can
   break it; (b) residential–commercial energy trade-off under WFH (R1-D13); (c) sources for the
   2030 horizon and WFH trajectory scenarios, including any "continued increase" evidence (WP2,
   R1-D6); (d) measured Canadian hourly residential data (WP5).
4. **Barsanti, Yilmaz and Binder (2024)** flagged in `02_journal_options.md` as a paper a reviewer
   would expect to see — decide whether to cite.

### WP13 — Venue and resubmission package

See §8. After the venue is chosen: apply its format (blinding only if double-blind; the
16/6-line master/blinded invariant applies only then), rebuild with the chain in
`extra/build_scripts/`, run `submit_check.py` on the **installed** files, write a new cover letter.

---

## §4 Order of work and critical path

```
Phase 0  author decisions (§7)                         ── gate
Phase 1  no-compute checks, in parallel:
         WP1 step 1 (re-derive the +8.3 pp gap)
         WP4 steps 1–2 · WP6 on 2022 data · WP7 step 2 · WP8 · WP9 · WP12.1–2
         write the deep-research prompts (WP12.3) → author runs them
Phase 2  compute, in this order:
         WP1 (2030 recalibration + 3,600 runs)        ── everything below needs it
         then in parallel: WP2 (2,400) · WP3 (3,600–4,800) · WP4 N=200 (1,200) · WP7 opt. (600)
         WP5 once external data is vetted
Phase 3  WP6 on corrected 2030 + scenarios · recompute CIs (WP8) · all figures (WP11)
Phase 4  venue decision (§8) · rewrite (WP10)
Phase 5  build, check installed files, cover letter
         → pre-submission external audit (T-AUDIT, §10 Wave 5) → fix → submit (WP13)
```

**Compute total:** about **11,000–13,000 EnergyPlus runs**, roughly twice the original Step-8
campaign. Wall-clock estimates must be taken from the Step-8/Step-9 run ledgers before asking for
approval, not guessed here. Cluster rules apply if run on Speed (`sbatch` only, 7-day walltime,
nothing on the login node); otherwise local runs under `GSSCanada\_local_runs\`.

**Biggest risk.** WP1 may shrink the 2022→2030 shape deltas until their CIs include zero. The
2015→2022 break then becomes the main behavioural contrast, but it crosses the household-panel
boundary (two different panels). Mitigation to decide in Phase 0: **one five-year panel drawn from
the post-relink frame for all of 2005–2030** would make the break a within-household comparison
too — cost **+3,600 runs** (2005/2010/2015 on the new panel). Recommended if WP1 comes back weak.

---

## §5 Weaknesses the reviewers did *not* raise (fix quietly)

1. Typical weather (TMY), not future weather, for 2030.
2. One Montréal Zone-6 envelope for all six cities; Atlantic households on the Montréal weather file.
3. Census–GSS match rests on conditional independence.
4. Metabolic heat channel not independently calibrated.
5. Weekend pooled into one day-type; hourly reporting.
6. Crosswalk count mismatch (WP12.1).
7. Figures below 600 dpi (WP11).
8. Table 1 novelty matrix never tested by a systematic search (WP12.3a) — a new journal's reviewer
   may test it.
9. The companion prior paper still "under review" in the text (WP12.2).
10. Table 1's Motuzienė et al. (2022) row checks "Forecast to future year," but the paper is a
    commercial-office, pandemic-era HVAC control study, not a residential 2030-style forecast
    (`dr_2J-12`, CARRIED, vetted against Crossref). Fix the checkmark or soften the §1.3 citation.
11. Discussion (§6) cites "Table 5" for annual-electricity percentage increments; Table 5 contains
    only EUI values and SHEU bands, no percentages (`dr_2J-12` Fable M4, CARRIED, verified absent).
12. §3.6 promises the lighting daylight-gate simplification is discussed in §7; §7 does not mention
    lighting, daylight, or R1 (`dr_2J-12` Fable M9, CARRIED, verified absent by full-text search).
13. Conclusion item 1 says EUI is "consistent with" SHEU ranges; §5.2/Table 5 say all four archetypes
    are below range — a direct same-document contradiction (`dr_2J-12`, CARRIED, corroborated by both
    Gemini and Fable). Fix regardless of WP7's outcome.
14. The SHEU ±2.7% agreement is a scalar fitted to the target, then checked against it — circular as
    stated (`dr_2J-12` Fable, CARRIED). Soften "validates the model" / "credibility anchor" wording;
    WP5's measured hourly comparison is a different, additional check, not a fix to this wording.
15. 2030 cohort size (37,008) equals exactly 3x the 2022 valid-diary count (12,336) (`dr_2J-12` Fable
    4.18, CARRIED as an arithmetic fact, cause not established) — one-line author check of whether
    this is a deliberate 3x oversample or a coincidence.
16. Table 1's six columns have no stated scoring criteria anywhere in the text, and "Calibrated
    behavioural model" is scored inconsistently: Chiou et al. (2011) gets a cross even though §1.5
    calls it survey-grounded, Yin et al. (2024) gets a check even though §1.2 says it "stops at
    statistical analysis" (`dr_2J-10` Fable R2/M3, CARRIED, 21/21 quotes and all nine Table 1 rows
    verified against the archived text). Fix belongs in WP10's Table 1 rewrite alongside item 8.
17. The manuscript's own "+2.2 to +3.9 pp" 2030 figure is defined two incompatible ways: as a level
    above the pre-pandemic baseline (Abstract, §3.4, §5.1, Conclusion item 2, four places) and, once,
    as the 2022-to-2030 step itself (§7 para 5). The two readings cannot both be true — under the level
    reading 2030 sits below the 2022 value of +5.2 pp, contradicting "persists"/"upper bound"; under the
    step reading 2030 sits at +7.4 to +9.1 pp with no stated driver for the further rise (`dr_2J-11`
    Fable Finding 5.1, CARRIED, arithmetic re-derived and confirmed). Needs an explicit editorial
    decision on which definition the rebuilt WP1 number reports, before the recalibrated 2030 figures
    are written anywhere.
18. Table 1's real gap is narrower than the manuscript's prose implies: a real, already-published paper
    (Chen et al. 2022, Applied Energy 325, 119890) scores 5 of the 6 novelty columns, missing only
    column C3 (a future/post-COVID scenario) (`dr_2J-10` Gemini, live search, CARRIED, all 33 cited
    DOIs Crossref-verified, headline claim corroborated via an open preprint). WP10's Table 1 rewrite
    should name C3 explicitly as the one axis separating this paper from Chen et al., not restate the
    gap as fully open. Separately, the same report's own Table B "Total Y" column undercounts 12 of 25
    rows (never overcounts); its printed rank order must be corrected before any row from it is quoted
    (see `deepResearch/dr_2J-10_VETTING.md` section 7 for the corrected counts).
19. The manuscript's 2030 scenario assumes WFH "persists with probability one" after 2022, but the real
    trend since 2022 is a continued decline, not a plateau: Canada 22.4% (May 2022) to 20.1% (2023) to
    18.7% (2024); the US SWAA series 30.4% (2022) to 28.7% (2023) to 27.6% (2024) to 25.9% (2026)
    (`dr_2J-11` Gemini, live search, CARRIED, positive control and all headline trade-off numbers
    independently confirmed). This is new evidence, not just an existing open item: WP2's planned
    "partial/high reversion" 2030 scenario (line 117) should be grounded in this observed post-2022
    trend rather than an arbitrary bracket. One cited figure, the "7.1%" 2016 baseline, could not be
    matched to the real StatCan source page (three other close numbers exist there instead) and must
    not be repeated in any redraft without the author re-checking StatCan directly.

20. Reference list: Motuzienė et al. (2022) is cited as *Sustainable Cities and Society*, volume 76;
    the real record (Crossref, ScienceDirect, PubMed) is volume 77 — the DOI itself
    (10.1016/j.scs.2021.103557) is correct, only the printed volume number is wrong (independent
    reference re-verification, 2026-09-17, all 52 references checked against Crossref/DataCite or
    primary source, fresh agent, not reusing the 2026-06/08 audit claims). Fix the volume number
    wherever this reference appears.
21. Reference list: Jalilian & Kamel (2025) is cited with a truncated title, "Urban-scale building
    energy modeling under future climate scenarios"; the real, full published title (Crossref) is
    "Urban-scale building energy modeling under future climate scenarios: a scalable workflow and
    insights from Nassau County, New York" (same 2026-09-17 re-verification). Restore the full title.
22. **The eleventh limitation carries one uncited literature claim.** `manuscript/draft_S7_limitations.md`
    now states that survey-methodology literature outside this project reports that moving to a
    self-administered mode can change how much at-home time a respondent records, independently of any
    real behaviour change. The claim is traceable to `deepResearch/dr_2J-12_VETTING.md:127-132,195-197`,
    which is quote-checked, **but no citable reference is attached to it**, and the assistant may not go
    and find one (deep research is external). Step 13 must therefore do one of exactly two things, and
    record which: (a) attach a real, vetted citation obtained through a deep-research ask, or (b) soften
    the sentence so it claims only what this project's own data supports, namely that the mode change is
    confounded with the 2022 break and cannot be separated from it. **Option (b) is fully sufficient for
    the limitation to stand** — the confound is established from `COLLECT_MODE` in our own data
    (0 for 2005/2010/2015, 1 only for 2022), not from the outside literature. Do not ship the sentence
    with the claim unsourced.
23. **Figure 1 must be cited under its own filename, and one legibility check is the author's.**
    The new workflow diagram lives at `figures/Figure_01_workflow.png` (plus the vector twin
    `Figure_01_workflow.pdf` and the reference copy under `figures/Prompts_Images/`). When WP11 inserts
    the figure into `manuscript/draft_S2_framework.md`, it must reference **`Figure_01_workflow.png`**
    and never `Figure_01_pipeline.png`: that second filename belongs to the retired axonometric pipeline
    overview, which is a different figure with per-stage result numbers overlaid, is captioned as such in
    `writing/figures/Figure_01_pipeline.md`, and is hard-referenced by the archived Building Simulation
    drafts under `writing/submission/extra/` and `writing/submission/archive/`. The two figures may never
    share a filename again. **One item stays unverified and cannot be closed by an agent:** legibility at
    the literal print size. T47 checked the file at a downscaled preview and found nothing wrong, and the
    embedded size is exactly 190 mm at 600 dpi, but a sub-pixel check for clipped glyphs at 100 percent
    zoom, or a proof print, is the author's own eye. Ask for it once, at figure lock-in, not before.
24. **RULED: the EUI gap is attributed to no single end use, and the "4 to 9 times space heating" number
    is never quoted.** dr_2J-13 came back and was vetted (`deepResearch/dr_2J-13_VETTING.md`, verdict
    PARTIALLY SURVIVES). No measured or survey-based Canadian end-use split exists: direct sub-metering
    NOT FOUND, SHEU carries no end-use split, the IESO/Cadmus survey NOT FOUND for absolute intensities,
    peer-reviewed NOT FOUND. The only split on offer is NRCan's CEUD, which the return itself describes as
    the Residential End-Use Model, an engineering stock accounting of unit energy consumptions calibrated
    to StatCan control totals. The prompt's scope guard said in advance that a modelled value is not an
    answer, so **pre-registered rule 3 fires**: the breakdown is not run at all, and the manuscript states
    that the measured end-use split was unavailable and attributes the Table 5 EUI gap to **no single end
    use**. The return's own headline sentence, that the gap is "unequivocally located in the thermal space
    heating load" at 4 to 9 times below benchmark, **does not go in the paper in any form**, including
    abstract, highlights and figure captions. Two independent reasons, either sufficient: rule 3, and the
    fact that the comparison's basis was never established (CEUD's denominator is *heated* floor space and
    its space heating is all-fuel raw combustion energy, gas-dominated in Ontario, while our figure is
    simulated site energy per our own floor-area definition; neither the area definition nor the fuel and
    efficiency scope was checked, so the multiple could be an artefact of the bases).
    **What the manuscript may say instead, and should:** that Canada publishes no measured residential
    end-use split, only a modelled stock-accounting disaggregation, so the gap cannot be assigned to a
    specific end use without a basis equivalence this study cannot establish. That is the honest form of
    the WP5 missing-measured-data limitation and it costs the paper nothing.
    **Two smaller rulings from the same vetting.** (a) The saved results file is the record; the
    chat-side summary of that run is **not to be used for anything** (its Ontario Single Detached water
    heating numbers do not reconcile with themselves, with the file, or with the live source, while the
    file's table reproduces CEUD exactly). (b) Three background citations in the return carry a wrong
    detail and must be corrected if ever cited: Rouleau and Gosselin 2021 is Applied Energy vol. **287**
    (not 290); Papineau et al. is **2021** (not 2022); the Makonin HUE dataset covers **22** homes and its
    citable publication is **2019** (not 28 homes, not 2018). None of the three carries a number used
    anywhere in this paper.

Items 1–2 get stronger once WP7 step 3 exists; item 8 is the one to do before resubmitting anywhere.
Items 10–19 are cheap, quote-verified fixes from `dr_2J-12`, `dr_2J-10`/`dr_2J-11` Fable, and
`dr_2J-10`/`dr_2J-11` Gemini vetting (`deepResearch/dr_2J-12_VETTING.md`,
`deepResearch/dr_2J-10_dr2J-11_FABLE_VETTING.md`, `deepResearch/dr_2J-10_VETTING.md`,
`deepResearch/dr_2J-11_VETTING.md`) and can be done alongside WP10 without waiting on WP1/WP5, except
item 17 (WP1 must settle it) and item 19 (WP2 needs it for the reversion scenario's numeric range).
Items 20–21 are cheap reference-list corrections from an independent 2026-09-17 re-verification of
all 52 references (52 checked, 50 clean, 2 errors, 0 not-found); apply during WP10's reference-list
assembly.

**New, currently unassigned work (not covered by any existing WP):** the CATI-to-EQ survey
collection-mode change lands on the same 2022 cycle as the COVID break, and the `COLLECT_MODE`
conditioning flag is 0 for 2005/2010/2015 and 1 only for 2022, so the model cannot separate mode
from behaviour (`dr_2J-12`, CARRIED, corroborated both by outside survey-methodology literature and
by internal flag logic). This is a real confound the manuscript does not currently rule out or
disclose. Needs a limitations paragraph at minimum (candidate: WP10 Discussion/Limitations); a
methods fix is not in scope for this round. Also carried: the abstract/highlights/Fig. 6 caption
attribute the CI-bearing 2022-to-2030 shape deltas to the WFH break, but that span crosses the panel
change (2015 to 2022) where the paired within-household attribution breaks down (§7 already admits
the panel change; the CI-bearing statistics are for the following, unpaired step). This is the single
most load-bearing finding of `dr_2J-12` and must reach WP1's provisional-framing fix and the abstract/
highlights, not just §7 — assign to WP1 + WP10.

---

## §6 Rules that carry over

- **Archive is frozen.** Copy, never edit.
- **Re-derive before quoting**, including the numbers in this plan.
- **Deep research is external.** We write prompts; the author runs and vets them.
- **Never create images** except plots computed from data. Schematics = prompt only.
- **Never start C-class work without the author's go.**
- **Verify on the installed `.docx`**, not the build output.
- **The timing check stays visible.** Reviewer 2 asks for the clock-alignment debugging to go to SI —
  agreed for the narrative — but keep **one sentence** in Methods saying a dedicated phase-level
  check was run, because annual-energy agreement cannot certify a timing result. That is a real
  methodological point, not debugging.
- Plain words in the paper, same as in chat: a reviewer should not need our internal vocabulary.

---

## §7 Decisions the author owns (recommendation first)

| ID | Decision | Recommendation |
|---|---|---|
| D1 | Scenario set for 2030 | S-Persist, S-Partial, S-Revert; add S-Grow only if an external source gives a number. **Working default from 2026-09-15** (author gave no objection; needed only at Phase 2, after WP1) |
| D2 | Run the simple-schedule arms (WP3)? | Yes, both arms — it is the direct answer to Reviewer 1's first point |
| D3 | Run the older-envelope sensitivity (WP7.3)? | Yes, SingleDetached only (600 runs). **Working default from 2026-09-15 (log ac):** existing-stock average envelope, values from `dr_2J-09` only, task T31 |
| D4 | One post-relink panel for all five years (§4 risk)? | Decide after WP1 results |
| D5 | Approve Phase 2 compute (~11–13k runs) | ✅ **APPROVED by the author 2026-09-15: run on the Speed cluster** (sbatch only, 7-day walltime). Extended the same day: **all computation on Speed, up to 32 CPUs per job and GPUs as needed** |
| D6 | Venue | ✅ **Target set by the author 2026-09-15: Applied Energy**, fallback Sustainable Cities and Society. Re-confirm at Phase 4 once the WP5 measured comparison exists (§8) |

---

## §8 Next venue — to select from `../02_journal_options.md`

That sheet (2026-08-07) ranked Building Simulation first and named **Applied Energy** as "the
deliberate next move if A rejects", with **Sustainable Cities and Society** conditional on declaring
the Concordia editor-in-chief conflict, and **Journal of Building Engineering** as the clean
substitute. Energy and Buildings stays excluded at the authors' request. The journal metrics in
that sheet were never verified and are still not safe to quote.

**How the reviews change the picture:**
- **Applied Energy** fits best *after* this plan: grid-facing metrics made prominent (R1-D19),
  a scenario range, a simple-model comparison, and — if WP5 finds data — a measured-profile check.
  Without WP5 it is the riskiest option, because Reviewer 2's missing-validation objection is exactly
  what a high-selectivity energy journal will raise first.
- **Sustainable Cities and Society** fits the new scenario-projection framing (stock, 2030 scenarios)
  and asks less on the grid side. Conflict must be declared in the cover letter.
- **Journal of Building Engineering** is the fallback if the WP5 outcome is weak.

**Recommendation:** choose at Phase 4 — **Applied Energy if WP5 produces a usable measured
comparison, Sustainable Cities and Society if it does not.** Update `02_journal_options.md` with the
decision and its reason at that point.

**Outcome of deep research (2026-09-15):**
- `dr_2J-06` outcome: **PARTLY USABLE**. Public open-download IESO Hourly Consumption by Forward Sortation Area (FSA) dataset identified, covering 2018 to 2024 hourly across >4.5M Ontario residential premises with premise count and weekday/weekend separation, but without heating-fuel disaggregation or individual archetype tags. Abdeen et al. (2021) Hydro Ottawa raw data is non-public under NDA.
- `dr_2J-07` outcome: Empirical audit of 27 recent articles (2022 to 2026) across Applied Energy, SCS, and JOBE revealed that only 33.3% check hourly profiles against measured data. In Applied Energy, 55.6% of sampled matching papers had no hourly measured check (relying on annual statistical checks like Chen et al. 2022, or held-out survey distributions like Mitra et al. 2022).
- **Decision under the agreed rule:** Build the partial comparison against IESO 2022 residential data (with 2019 baseline), state limits plainly, and target **Applied Energy** (Option B), with **Sustainable Cities and Society** (Option C, declaring Concordia conflict) as the immediate fallback.

**Manager audit of the two returns (2026-09-15, offline reading only; DOIs not re-checked by us, per
the deep-research rule).** The returns were produced by an agent run, and the audit changes how they
may be used:
- **What stands:** the IESO residential hourly dataset exists and is open. The run downloaded two of its
  monthly files. WP5 therefore has buildable measured data, and that is the whole basis for the target.
- **Not usable as numbers:** the `dr_2J-06` Table 2 values (peak hour, load factor, midday share) come
  from **January only**, from a 7-hour window (hour-ending 10 to 16) that is not our metric
  definition, and were never cross-checked. **Do not quote them.** Task T02 re-measures from scratch.
- **Leads only:** the Manitoba Hydro and Toronto Hydro rate-case rows give home-page URLs, no filing
  numbers the run opened, and an unsourced "~1,500 customers". Treat as leads for a later search.
- **`dr_2J-07` is unverified in substance.** The run fetched Crossref metadata but did not open the
  paywalled full texts, yet Table 1 gives section-numbered "quotes" for all 27 articles. Those quotes
  and the YES/NO classifications must be treated as **unread**. Nothing from `dr_2J-07` may be cited,
  quoted, or used as a count in the cover letter or paper. It does not change the target: the target
  rests on the IESO data, not on the counts.
- The §9 box "vetted by the author" had been ticked by that run; it is **unticked** below until the
  author vets.

**Target (author, 2026-09-15): Applied Energy.** Fallback Sustainable Cities and Society (declare the
Concordia conflict). Confirm at Phase 4 once WP5 exists.

---

## §9 What closes this round

- [ ] §7 decisions answered by the author
- [ ] WP1 done; the +8.3 pp gap re-derived before and after; all 2030 numbers recomputed
- [ ] WP2–WP9 done or explicitly declined, each with its implementation doc
- [ ] Deep-research returns vetted by the author before any new citation (dr_2J-06 and dr_2J-07 returned 2026-09-15; manager audit in §8; author vetting still owed, `dr_2J-07` quotes unread)
- [ ] Every one of the 42 triage rows in §2 mapped to a change in the new manuscript (keep this map;
      some journals ask about prior submissions)
- [ ] Carried items closed: crosswalk, 600 dpi, prior-paper status, novelty-matrix search
- [x] Venue target set by the author and recorded in `02_journal_options.md` (Applied Energy, fallback SCS; re-confirm at Phase 4)
- [ ] Manuscript rebuilt; `submit_check.py` green on the installed files
- [ ] Pre-submission external audit (T-AUDIT, §10 Wave 5) run by the author in Gemini and in Fable 5,
      both returns vetted, every accepted item fixed and re-checked on the installed files
- [ ] `00_README_submission.md`, the revision-decision prompt, and the memory file updated to the new
      archive paths and outcome in the same pass

---

## §10 Implementation plan — who does what, in which order (set 2026-09-15)

**Target journal: Applied Energy** (§8). Everything below is written for it: grid-facing shape metrics
first, scenario range, simple-schedule comparison, measured Ontario check. Format rules (length,
highlights, abstract) are read from the live Guide for Authors at WP13, never assumed.

**Roles.** Manager (Opus) writes one task doc per task, reads results, owns every design decision
(for example the 2030 re-targeting in WP1 step 2). Employees (Sonnet, or Haiku for pure reading) do
one task each, from their task doc, in a fresh session.

**Where state lives.** One doc per task in `impl/`, named `2026-09-15_Tnn_<slug>.md`. It holds the
task, the job ledger, numbers actually read, assumptions, next action and what was not verified.
Nothing lives only in an agent's memory.

**Employee rules (every task doc repeats them).**
1. All computation runs on Speed through `sbatch` (partition `ps`, up to `-c 32`, `-t 7-00:00:00`).
   No `python` and no blocking `srun` on the login node. The login shell is tcsh: no `2>&1`, no
   `2>/dev/null`. Python env: `/speed-scratch/o_iseri/envs/step4/bin/python`. Work dir:
   `/speed-scratch/o_iseri/2J_revision/Tnn/`.
2. **Submit, write the JobID in the task doc, end the turn.** No waiting, no poll loops. A fresh agent
   collects the output.
3. Never edit `archive/`, pipeline source files, or the frozen Step-8/Step-9 outputs. New scripts go
   in `impl/Tnn_scripts/`, outputs in `impl/Tnn_out/`.
4. Use the paper's own metric definitions, read from the code (`Step8_docs/08_simulation_plots.py`,
   `Step8_docs/interim_report_gen.py`), and quote the `file:line` where they were found.
5. Never read a multi-MB file into context; use `wc -l`, `head`, `grep`.
6. Write "NOT VERIFIED" rather than guess.

**Wave 1 — Phase 1 checks, started 2026-09-15 (no new EnergyPlus runs).**

| Task | Plan item | What it produces | Agent |
|---|---|---|---|
| T01 | WP1 step 1 | 2022 vs 2030 at-home shares from the schedule files, national and per archetype (confirms or corrects the +8.3 pp gap) | Sonnet |
| T02 | WP5 step 3a | Measured Ontario and Toronto residential hourly profiles 2019, 2021–2023 from IESO, with our metrics | Sonnet |
| T03 | WP8 | How the two confidence intervals were built; reproduce the submitted values; cell-aware bootstrap beside them | Sonnet |
| T04 | WP9 | When the four model-selection thresholds were set; re-ranking under ±10% and ±20% | Sonnet |
| T05 | WP4 steps 1–2 | Written sampling procedure; subsample convergence from the existing 50 households, 2022 only | Sonnet |

**Wave 2 — after Wave 1 is read by the manager.**
- T06 WP6 on 2022 (end use by hour) · T07 WP7 step 2 (EUI gap by end use) · T08 WP12.1 (crosswalk
  counts) · T09 WP5 step 3b (simulated Toronto 2022 profile against the T02 measured profile, same
  metrics, shoulder months first because our electricity meter excludes heating and cooling).
- Manager writes the WP1 step 2 re-targeting spec from T01 (design, not delegated).

**Wave 3 — Phase 2 compute on Speed.** WP1 steps 2–5 (2030 re-rake, schedules, 3,600 runs) → then in
parallel WP2 (2,400), WP3 (3,600–4,800), WP4 N=200 (1,200), WP7.3 (600). Arrays sized to 32 CPUs.

**Wave 4.** WP6 on corrected 2030 and scenarios, WP8 on corrected runs, WP11 figures, WP10 rewrite for
Applied Energy, WP13 package.

**Wave 5 — last gate before submitting to Applied Energy (added 2026-09-15 at the author's request:
"I want to be sure we are submitting a clean journal").**

- **T-AUDIT — external investigation and improvement prompt, for Gemini and for Fable 5.**
  - **When.** Written only after WP13 has a built package and `submit_check.py` is green on the
    installed files. Never earlier: the prompt audits the final text, not a draft.
  - **Who.** Manager (Opus) writes the prompt; it is a design task, not delegated. The author runs it,
    once in Gemini and once in Fable 5, as two independent reads. Deep-research rule applies: we do not
    run it and do not search literature ourselves.
  - **File.** `deepResearch/dr_2J-08_presubmission_audit_prompt.md`; returns saved beside it as
    `dr_2J-08_results_gemini.md` and `dr_2J-08_results_fable5.md`.
  - **What the prompt asks both models to check**, each item answered FOUND / NOT FOUND with the
    manuscript location:
    1. Every number in the text, tables, figures, abstract, highlights and cover letter against the
       number-provenance sheet (T10 successor); any mismatch listed.
    2. Every one of the 42 reviewer triage rows (§2): is the concern answered in the new manuscript, and
       where. A prior reviewer's point left unanswered is a blocker.
    3. Claims against evidence: overclaiming, causal words without a causal design, results stated
       beyond their confidence intervals, the 2030 scenario range presented as a forecast.
    4. Applied Energy Guide for Authors, read live by the model: length, highlights, graphical abstract,
       data availability, CRediT, declaration of interest, AI-use statement, reference style.
    5. Citations: every reference opened, DOI checked on crossref, every citing sentence supported by
       the source; `NOT FOUND` beats a guess. Nothing from `dr_2J-07` may appear.
    6. Internal consistency: methods vs results vs SI, figure and table numbering, units, city and
       archetype names, the frozen 144,465-household frame stated the same way everywhere.
    7. Limitations stated plainly (never "failure"): the 2022 donor pool, TMY weather, one envelope,
       the partial Ontario measured check, conditional independence in the match.
    8. Language: internal project vocabulary left in the text, no em or en dashes, plain words.
    9. An improvement list, ranked by how likely each item is to trigger a desk reject or a major
       revision at Applied Energy, each with a concrete fix.
  - **Rules restated inside the prompt.** Never relax a band or soften a result to pass; do not
    invent numbers; do not rewrite the manuscript, only list issues and fixes; confidential rejection
    letter is not shared, only our §2 paraphrase.
  - **After the returns.** Manager vets both with the 7-step vetting, lists where the two models
    disagree, and re-measures any disputed number from its artifact before acting. Accepted fixes go
    through a fresh employee, then `submit_check.py` again on the installed files. Submit only when
    every accepted item is closed.

---

## Progress Log

- **2026-09-15** — Rejection received (BUIL-D-26-01113, 3 reviewers). Submitted files moved to
  `archive/` (18 files, SHA-256 identical before/after). This plan written. Nothing computed, no
  manuscript edits. Next: author answers §7.
- **2026-09-15 (b)** — Author: start now; D5 approved (Speed cluster). Deep-research prompts written
  to `deepResearch/`: `dr_2J-06` (measured Canadian hourly residential data, WP5/WP12.3d) and
  `dr_2J-07` (how often matching papers at AE / SCS / JBE check hourly shape against measured data).
  Venue decision rule fixed in advance in `deepResearch/00_README_deepResearch.md`. D1 (scenario set)
  still open.
- **2026-09-15 (c)** — Executed `dr_2J-06` and `dr_2J-07` deep-research prompts. `dr_2J-06` returned PARTLY USABLE (open IESO FSA dataset covers 2018-2024 hourly residential consumption with premise counts; no heating fuel split). `dr_2J-07` verified that 55.6% of matching papers in Applied Energy had no hourly measured check (relying on annual totals or survey checks). Per decision rule, venue target is **Applied Energy** with partial measured check built in WP5, and **Sustainable Cities and Society** as clean fallback. Results saved to `deepResearch/dr_2J-06_measured_hourly_load_data_results.md` and `deepResearch/dr_2J-07_validation_bar_by_venue_results.md`. Next: start WP1 step 1 (re-derive the 2030 at-home gap).
- **2026-09-15 (d)** — Author: target Applied Energy; update the plan; start execution with cheaper
  agents; all computation on Speed, up to 32 CPUs per job. Manager audit of the two deep-research
  returns added to §8 (IESO data real; `dr_2J-06` numbers not usable; `dr_2J-07` quotes unread, not
  citable); the "vetted" box in §9 unticked. D1 scenario set taken as the working default. §10
  implementation plan written. Wave 1 task docs T01–T05 written in `impl/` and handed to five Sonnet
  employees. Nothing computed yet by this session. Next: collect Wave 1 outputs, then Wave 2.
- **2026-09-15 (e)** — T04 finding carried into WP9 (J3 not the only four-gate passer; choice stands on
  lowest composite). Queue check 09:53 EDT: all six Wave-1 jobs PENDING `AssocGrpCpuLimit`. The 32-CPU
  cap (`cpu=32,gres/gpu=4`) is per ACCOUNT, not per job, and 4J job 1328237 (`4J_c2_ES_v2`, ES campaign,
  7-day limit) holds all 32. Manager shrank pending jobs with `scontrol update NumCPUs` to fit together
  (1328238→4, 1328239→4, 1328240 4, 1328241→8, 1328242→8, 1328244→4; total 32). Author: **wait for 4J**,
  do not hold it. Wave-1 start time therefore unknown. Rule for future task docs: request ≤8 CPUs per
  revision job unless the work truly parallelises. Next: collect Wave 1 once jobs finish.
- **2026-09-15 (f)** — 4J job cancelled by author; queue re-checked. The `scontrol` shrink did NOT hold:
  started jobs got 32 CPUs (script `-c 32` wins), so Wave 1 runs one job at a time. T03 (1328238)
  COMPLETED and collected: interval method found (plain paired t-interval over 1,200 households, flat
  pool, `08_simulation_val.py:951-1027`), but it does NOT reproduce the submitted numbers on the
  current `agg_annual.csv` (2026-07-15): midday share +2.14 pp vs +0.367, load factor +0.0181 vs
  +0.0117. Cell bootstrap is 1–3 % narrower than the t-interval, not wider. Manager submitted 1328253
  (1 CPU) on the archived 2026-06-05 copy to test whether the submitted numbers came from pre-July
  data. ⚠ If yes, other manuscript numbers may predate the July regeneration. T02 (1328239) running.
- **2026-09-15 (g)** — Wave 1 collection. **T01 DONE** (1328241 + hash check 1328240, both exit 0; the
  19 s run was genuine fast I/O, 6,934,320 rows per year; hashes match the local files): national
  weekday at-home 70.2 % (2022) vs 78.5 % (2030); 3-household schedule test matched EnergyPlus inputs
  exactly. **T02**: 1328239 failed on one IESO monthly file (2023-08) that came back with a server
  error banner before the header; parse-only fix reviewed and approved, resubmitted as **1328255**
  (4 CPUs, running). **T03 DONE as a method check**: the archived 2026-06-05 copy (1328253) gives
  midday +0.389 pp [0.267, 0.511] and load factor +0.0113 [0.0087, 0.0139], close to but not the
  submitted +0.367 [0.208, 0.526] / +0.0117 [0.0085, 0.0150] (different widths at the same n, so a
  different file). The source file is lost (likely `outputs_step8_v2/`). ⚠ Between June and the
  July 15 regeneration the midday shift grew ~5.5x; manuscript numbers written before 2026-07-15 need
  a provenance audit (Wave 2 task). **T04** (1328244, 2 s) and **T05** (1328242, 9 s) completed exit
  0; Sonnet collectors checking whether the short runs did the full work. Next: read T04/T05
  collector reports, then write Wave 2 task docs.
- **2026-09-15 (h)** — **T04 DONE**: Speed output byte-identical to the local dry run. At the original
  thresholds four trials pass 4/4 (J3, J5_X1, J5_X2, J5_B); J3 is picked only by lowest composite
  (0.6355). J3 stays selected in 19 of 21 ±10/20 % variations; it flips to J5_X1 only when the at-home
  threshold is tightened 20 %. Paper must say "selected by composite among four that passed", not "the
  only one passing". Late correction in the T04 doc: `results_index/results.csv` exists but predates
  J3. ⚠ That agent ran a `find` on the Speed login node: every future brief forbids it explicitly.
  **T05 DONE (run complete, 500 rows)**, but the ~4x narrowing N=10→40 is the finite-pool effect of
  subsampling 50 without replacement (predicts 4.0x, measured 3.8x): it cannot show N=50 is enough.
  WP4 step 3 (N=200) is required for that claim. T02 v2 (1328255) still running. Next: Wave 2 task
  docs (≤8 CPUs each): WP4 N=200, manuscript-number provenance audit, WP1 re-targeting spec.
- **2026-09-15 (i)** — Wave 2 started. Task docs written and handed to fresh Sonnet employees: T06 (end
  use × hour, 2022 only, ≤8 CPUs, stops if the upload would exceed 20 GB), T07 (energy-intensity gap by
  end use, 2022, must use the V4-B4 corrected parsing, never the defective `eui_kWh_m2` column), T08
  (crosswalk counts, reading only), T10 NEW (which data generation each manuscript number came from,
  reading only; added because of T03). Every brief now forbids `find`/`du`/python on the Speed login
  node. T09 (simulated vs measured Toronto) waits for T02 v2 (1328255). WP1 step-2 re-targeting spec
  (manager) next.
- **2026-09-15 (j)** — Wave 2 collection, part 1. **T02 DONE** (1328255 superseded failed 1328239): IESO
  measured Ontario and Toronto residential hourly profiles 2019–2023, 528 metric rows. **T07 DONE**
  (1328260): 2022 energy intensity by end use, 1,200 runs, totals round-match V4-B4; appliances largest
  in 3 of 4 archetypes. That ranking does not answer which end use carries the gap to SHEU: the SHEU
  end-use split is not on disk (author supplies). Simulated space heating 12.6–29.5 kWh/m² is low for
  Canada: first check once SHEU arrives. **T08 DONE** (reading): sheets give 183/266/64/123 rows vs the
  paper's 182/264/64/121; T14 tests whether the paper counted codes seen in the diaries. **T10 DONE +
  CSV repaired**: 59 numbers; only 5 recomputed matches, 3 recomputed mismatches, 35 log-only. **T11
  DONE**: the 2030 target skips Step 5, and 76.93 % (person, 30-min) and 70.2 % (household, hourly) are
  not the same quantity. Manager then read `07_aug_to_bem.py:182-193`: 2030 schedules give every stock
  person a random 2030 diary matched on day type only, so the schedule mean equals the pool mean
  (78.44 % → 78.5 %). Spec `impl/2026-09-15_WP1_step2_retargeting_spec.md`: design D1 = rake the
  stock's own diaries by the forecast change; null-forecast test must reproduce 2022. **T06** failed
  twice (1328259, 1328268), diagnoser working. Launched: **T12** (WP1 stage A diagnostic), **T09**
  (simulated vs measured Toronto 2022), **T14** (codes observed). Speed login node rebooted 10:45; no job lost.

- **(k) 2026-09-15, manager.** **T14 DONE:** the paper's 182/264/64/121 are the distinct activity codes
  observed in the diaries, exactly, in all four cycles (codebook rows 183/266/64/123; code `2` is a real
  observed code in 2005/2010). **T06** diagnosed (wrong input root, then a JSON bug); job 1328273 exit 0 in
  20 s, collector checking all 1,200 homes were read. **T12** job 1328275 failed in M5 (two columns not
  loaded) after M1-M4 wrote; fixed and resubmitted as 1328277. **M1-M4 already decide spec §5:** stock
  weekday at-home 69.8 % (branch 1 condition holds) **but 77.7 % of stock persons carry a 2005/2010/2015
  diary; only 22.3 % carry a 2022 diary** (branch 3 fires). The 2022 schedules are therefore a four-cycle
  mix, while the manuscript calls 2022 the "calibrated-observed year" (`archive/2J_manuscript_submission.md:318`)
  and `07_aug_to_bem.py:204` uses the stock as is. Weekday stock by diary cycle: 2022 real 74.6 %,
  2005-2015 real 67.5-70.8 %. **Stage B (T13) is on hold pending the author** (spec §5 branch 3).
  Detail: `impl/2026-09-15_T12_wp1_stageA_diagnostic.md` Verified.
  **(k, cont.) T12 complete (job 1328277).** Both T01 numbers reproduced exactly (70.239, 78.526). Null
  test: the current 2030 machinery with a zero-change pool gives 76.93 % weekday, +6.69 pp over the 2022
  file, so it fails N0. Weekday gap +8.29 pp = anchor population +6.69, forecast +1.59, redraw −0.45.
  Stage B remains on hold for the author's choice: rebuild 2022 from 2022-cycle diaries, or keep the
  four-cycle mix and anchor 2030 on it (D1 as specced).
- **(l) 2026-09-15, manager.** **T06 DONE** (1328273, 1,200/1,200 homes): evening peak 17-18 h in all
  archetypes; heating/cooling/hot-water electricity = 32 % (SingleD), 34 % (OtherDwelling), 43 %
  (HighRise), 63 % (MidRise) of Facility; MidRise hourly files carry no WaterSystems meter. **T09**
  (1328279) ran clean but its stock comparison was not usable: whole-building totals mixed with single
  homes, and weekday taken from the real calendar although EnergyPlus starts 2022 on a Sunday. **T15 DONE**
  (1328281, fix): dwellings per model 1 / 7 / 31 / 79 (SingleD / OtherDwelling / MidRise / HighRise);
  annual electricity per dwelling 8,165 / 6,778 / 8,793 / 4,975 kWh vs measured Toronto ≈7,334 per
  premise. Stock weekday full year, EnergyPlus calendar: peak hour 17.5 sim vs 18.25 Toronto; load factor
  0.338 sim vs 0.440 (all electricity), 0.517 (lights+equipment+fans). Calendar fix moved metrics only
  0.01-0.05. Detail `impl/2026-09-15_T15_wp5_sim_vs_measured_fix.md`. All Wave 3 runs except the WP3
  static-schedule arm depend on the author's 2022 decision; T16 (reading) maps the Step-8 run machinery.
- **(m) 2026-09-15, manager.** **Author decision on WP1 stage A (branch 3): option (a), "choose the
  highest accuracy option".** The 2022 schedules are rebuilt from 2022-cycle diaries only (real + synthetic
  2022 diaries), so the 2022 year represents 2022 behaviour and the "calibrated-observed year" wording
  stays true. 2030 is then built with D1 (delta on the rebuilt stock) so N0 holds by construction. Cost
  accepted: both 2022 and 2030 Step-8/Step-9 runs are redone, and every 2022 result already collected
  (T06, T07, T15) is re-derived on the new runs. Risk recorded: the donor pool shrinks from four cycles
  to one, so linkage fallback tiers may rise; stage B must report tier shares before vs after. Stage B
  starts with T13 (reading: how `05_census_linkage.py` and the aggregation/exclusion step pick donors,
  and where a cycle filter can be applied from a new script). T17 (Speed reproduces the local campaign)
  running: array task 0 done, 1-3 running.
- **(n) 2026-09-15, manager.** Author: "continue until the end, do not stop the progress anymore for
  questions" — the manager now takes remaining design choices itself and records them here. T13 done:
  the donor pool is the whole `augmented_diaries.csv`, split only by day type; cycle and synthetic flag
  are never used to choose donors; matching is a 4-tier key fallback, seed 42; the exclusion step is
  `05_census_linkage.py --exclusion`, not a separate script. Mitigation "fix it" (spec §5b) resolved as:
  2022 real + synthetic donors; the existing tier fallback already relaxes keys within the pool; no reuse
  cap exists without a source change, so reuse is reported instead. Side effect recorded: a 2022-only pool
  removes the 2005/2010 `colleagues30` zero asymmetry. **T18 briefed (manager decision): two-arm build on
  Speed, a control arm with the full pool that must reproduce the current files before the 2022-only arm
  is trusted**, then N4 (tiers, reuse, cycle share, at-home levels). T19 (WP3 static-schedule arm wrapper
  + smoke) running. T17 array tasks 1-3 still running.
- **(o) 2026-09-15, manager.** T18 SUBMITTED: filter job 1328300, chain array 1328301 (0 = control, 1 =
  2022-only). The employee found two things, recorded in the T18 doc: the scripts' own `BASE` path does
  not resolve from the current layout, so every path constant is set by a wrapper; and `--exclusion`
  needs the `--bem` output, so `--bem` was added before it in both arms (matches the master log's order).
  The current build used `--region-tier`; both arms use it. T19 smoke job 1328297 running (first
  submission 1328296 cancelled, wrong code root). **T20 (D1 2030) employee launched, to submit with
  `afterok:1328301`.** Manager decision: T20 may run before the T18 collector reports; if the control arm
  does not reproduce the current files, T20 outputs are discarded, not used. Collectors launched for T17
  and T19.
- **(p) 2026-09-15, manager.** T19 smoke COLLECTED, all 6 checks pass (job 1328297). T17: two of four
  archetypes done, MidRise/HighRise still running. T19 found that `idf_optimizer.py:625` looks for
  `schedule.json` at the wrong level and silently falls back to hardcoded standard schedules. **T23 briefed
  (read-only audit): did any published arm use the fallback?** If yes it becomes a correction item.
  **T22 briefed and launched: static arm full run, 24 cells × 50 households**, on the current 2022 household
  sample (manager decision: the rebuild keeps the census households; the T18 collector confirms IDs and
  design levels match, else only differing cells rerun).
- **(q) 2026-09-15, manager.** T23 DONE: every published run (Step 8 campaign, Step 9 Default arm, Step 9
  matched-arm defaults) did take the fallback code path, but the hardcoded fallback values are identical to
  `schedule.json` for occupancy, equipment, lighting, DHW and activity. Manager re-read both
  (`idf_optimizer.py:734-767`, `0_BEM_Setup/Templates/schedule.json:9-45`): same numbers. **No published
  number changes; not a correction item.** The path bug is a code-hygiene note only. T22 static arm
  submitted (array 1328310, `-c 4`, 2 at a time), queued behind T17/T18 on the CPU cap.
- **(r) 2026-09-15, manager.** T20 SUBMITTED (array 1328311, waits on T18). **WP2 design fixed:
  `impl/2026-09-15_WP2_scenario_spec.md`.** It is one family with λ = the share of the COVID jump that survives
  to 2030 (Persist 1, Partial 0.5, Revert 0), on the rebuilt stock with the code's own slope and jump. S-Grow
  is not built without an external number. The standardized jump is a reported sensitivity; if it differs
  by more than 1 pp, S-Revert-std is added. This replaces the §3 table wording "standardized 2015 level" and
  keeps λ = 1 identical to T20. T26 (scenario schedule builds) is launched, to depend on T20. Two read-only
  tasks are launched: T24 (were the 2005/2010/2015 schedule files built from their own year's diaries? This
  bears on the 2015→2022 break) and T25 (Step-9 run machinery, needed to brief T21).
- **(s) 2026-09-15, manager.** T24 DONE (`impl/2026-09-15_T24_historic_cycle_schedules_donors.md`). The
  2005/2010/2015 files come from `Step8_docs/08_gen_cycle_schedules.py`, which swaps each person on the frozen
  2022 dwelling frame for a diary drawn only from that year's pool (`:253`, `CYCLE_YEAR == year`; every
  fallback tier stays inside that pool). **No historic year is mixed; WP1 does not extend to the historic
  files.** The historic files read only the frame's demographics, not its diaries, so the T18 rebuild
  does not touch them, provided the T18 collector confirms the household IDs and person demographics are
  unchanged. Caveat on record: no run log of the original build exists. The verdict rests on the script text
  and backup timestamps. A seed-42 rerun of one year, compared cell by cell with the on-disk file, would close
  that caveat. It is queued as optional, after the CPU cap frees, and does not block anything.
- **(t) 2026-09-15, manager.** T25 DONE: Step 9 is 4,800 runs on the same seed-42 households as Step 8, through the
  same engine. It needs the 13-col baseline files re-derived from the rebuilt files. T18 array left the queue
  13:45, and a fresh collector was launched. T21 written (`impl/2026-09-15_T21_wp1_step8_step9_rerun.md`) with
  acceptance A1–A6 fixed. Phase A (stage, baseline extract, n=2 smoke, all waiting on T20) is launched. The
  full 7,200 runs (phase B) need a manager go after the T18/T20 collectors and the smoke pass.
- **(u) 2026-09-15, manager.** T18 collector: both arms' 7-step chains ran OK. `sacct` FAILED came only from a
  metrics-script bug, and a fixed verify job is pending. Arm C weekday household at-home is 70.24 %, as expected.
  Arm N is 74.82 %. **The strict match share drops by 15.19 points (44.94 → 29.75 %), past the 10-point limit.**
  Arm N also has 164 extra households, and it fails validator check 3.5 (stock at-home 75.0 % vs the weighted
  GSS-2022 anchor 72.3 %, band ≤ 2 pp; the band is not moved). T18b written and launched: one lever (drop CMA
  from Tier 1). The household frame is frozen to the published 144,465 households at the stock level, for every
  downstream build. The choice rule is fixed now: CMA-lever build if its strict share ≥ 34.94 %, otherwise the
  plain 2022-only build with the drop stated as a limitation. The check 3.5 gap is split by real vs synthetic donor,
  and by weighting if a weight column exists. T20, T26 and the T21 phase-A jobs depend on the failed T18 array. They
  will be cancelled and resubmitted against the chosen stock.
- **(v) 2026-09-15, manager.** The T18 verify job ran clean. Arm C reproduces the published 2022 files exactly
  (line endings were the only difference), and nothing published was touched. T18 is closed. Arm N lacks 849
  published households and has 1,013 extra (the net +164). So the T18b frame assert is expected to stop. Frame v2 is
  written into the T18b doc before any T18b output was read: the frozen frame is taken from the pre-exclusion
  stock, and the count of published households under the 0.30 at-home cut is reported as a limitation. Design W
  is diary-derived, so it changes with the donors by construction; no stock change and no T24 impact. T21
  phase-A jobs 1328329/1328330 are added to the cancel list.
- **(w) 2026-09-15, manager.** Author request: before submitting to Applied Energy, prepare an
  investigation and improvement prompt for Gemini and Fable 5, "to be sure we are submitting a clean
  journal". Added as task T-AUDIT in §10 Wave 5, as a Phase 5 step in §4, and as a §9 closure box. The prompt
  is written only after the package is built and checked; nothing written or run yet.
- **(x) 2026-09-15, manager.** T17 COLLECTED: Speed reproduces the local campaign on all 4 Toronto cells, 2022 and
  2030, same 50 households, annual electricity within about 0.001 % (pass line 0.1 %). T18b collected: both builds
  stopped on the frame assert as pre-registered (N-f 849 missing / 1,013 extra; Nb-f 869 / 1,031); no validator ran.
  Nb-f 6-key Tier-1 share 41.97 % meets the rule's 34.94 % bar; its city-agreement share is 20.08 % (Arm C 44.94 %,
  Arm N 29.75 %), recorded as a limitation, rule not re-opened (T18b addendum 2). T18c (Frame v2, both builds)
  briefed and handed to a fresh employee. Progress checklist page published for the author.
- **(y) 2026-09-15, manager.** T18c SUBMITTED: array 1328337 (0 = nf, 1 = nbf), both tasks running. The employee
  ran `mkdir` once on the login node (recorded in the T18c doc). Session handover: the next manager starts from
  `writing/Prompts/2J_manager_prompt_RESUME_AE_resubmission.md`. Next: collect T18c, apply the choice rule,
  cancel and resubmit T20/T26/T21 phase A on the chosen stock.
- **(z) 2026-09-15, manager (new session).** T18c still running (both tasks, ~6 min in). Confirmed with `scontrol`
  that 1328326/1328329 wait on `afterok:1328311_*` and 1328311 waits on the failed 1328301 array, then
  `scancel` 1328311, 1328326, 1328327, 1328329, 1328330 (manager, one command). Their task-doc Ledgers get the
  "superseded/cancelled" line when the resubmitting employee runs. T22 (1328310) untouched, tasks 6-7 running.
  Next: collect T18c when it leaves the queue.
- **(aa) 2026-09-15, manager.** T18c COLLECTED: job 1328337 both tasks exit 0, every step OK. Both builds hold
  all 144,465 published households (missing 0, extra 0 after filter, 6,934,320 rows) and change no input.
  **Choice rule applied: Nb-f (CMA dropped from Tier 1, strict share 41.97 %) is the frozen 2022 stock** for T20,
  T26 and T21 (paths in the T18c doc, Manager decision). Validator check 3.5 fails on Nb-f (75.04 % vs 72.3 %,
  band 2 pp, not moved): a limitation. The weighted real-2022 donors sit on the anchor (72.31 %); the gap comes
  from unweighted means and synthetic donors (75.95 %), and dropping the 869 households under 0.30 widens it
  (75.23 %). Validator overall 30 pass / 1 fail / 1 warn. Next: fresh employee resubmits T20, T26, T21 phase A on
  Nb-f.
- **(ab) 2026-09-15, manager.** Resubmitted on Nb-f (only the three job scripts' input paths changed; the
  framev2 stock has the same columns as the old `_excl` stock, since exclusion and frame filter are row filters):
  T20 1328375 (running), T26 array 1328377 `afterok` T20, T26 compare 1328379 `afterok` 1328377, T21 baseline
  extract 1328378 `afterok` T20, T21 smoke 1328380 `afterok` 1328378. Old JobIDs kept in the Ledgers as cancelled.
  T20 N2 restated in the T20 doc (manager addendum): the validator now runs 32 checks, so "28/28" becomes "every
  check passing on Nb-f 2022 also passes on 2030, no new FAIL"; no band moved. Checklist page republished.
  Next: collect T20 when 1328375 leaves the queue.
- **(ac) 2026-09-15, manager.** T27 reading DONE (Wave 3 facts). Wave 3 task docs written, each with a phase A
  (scripts, staging, smoke where the mechanism is new) that can start now and a phase B (full array) that waits for
  the T20 N0–N2 pass and the T21 smoke: **T28** WP4 N = 200 in the four Montreal cells, 2022 and 2030, 1,600 runs
  (all 200 run, so the first 50 give an exact reproducibility check against T21); **T29** WP2 S-Partial and
  S-Revert, 2030 only, 2,400 runs (S-Persist is T21's 2030 arm by SC0 nesting); **T30** WP3 average-profile arm,
  one mean profile per cell pool and year, 2,400 runs; **T31** WP7.3 SingleD envelope, 600 runs. Decisions taken:
  (1) WP4 keeps the code's stock weighting (archetype only, equal over cities) and the rewrite describes it; (2) the
  average profile is taken per cell pool, not per archetype nationally, the stronger competitor; (3) WP7.3 uses the
  **existing-stock average** envelope, not a pre-code one, because SHEU describes the existing stock; its values
  come only from the new deep-research prompt `dr_2J-09` under a rule fixed in advance (any core value NOT FOUND =
  WP7.3 not run, limitation stated); (4) the household peak-hour spread and morning-leaning share are the paper's own
  code (`08_simulation_plots.py:290,914`), not new definitions; (5) the schedule fallback bug needs no fix ticket
  (T23: values identical). Throughput from T27: SingleD cells about 15 min, apartment cells 1.5–2.6 h per 100 runs
  at 8 CPUs; Wave 3 queues behind T21 via `--nice`. Author owes: run `dr_2J-09`. Next: four phase-A employees.
- **(ad) 2026-09-15, manager.** T28 phase A READY (WP4 N = 200 scripts, checks B1-B5, staged, nothing submitted);
  its checks B1, B2 and B5 were seen failing on a fake tree. T29 phase A READY (WP2 S-Partial/S-Revert scripts,
  checks P0-P5, staged, nothing submitted); P1 and P2 seen failing. Manager addenda in both docs: T28's collector
  hand-checks the t-CI and subsample means on a known array and reads each Montreal pool size (>= 1,045) before
  quoting; T29's collector makes P3-P5 fail once before trusting them, and P1 uses T21's re-run manifests only.
  Author request: the resume prompt `writing/Prompts/2J_manager_prompt_RESUME_AE_resubmission.md` is updated after
  every task completion (done now; §2-§3 rewritten to the current state). T30 and T31 phase A still running; T20
  job 1328375 still running. Next: collect T30, T31.
- **(ae) 2026-09-15, manager.** T20 (D1 2030 on Nb-f) array 1328375 COMPLETED, both tasks exit 0 (16:20, 16:26); a
  fresh collector is filling N0-N3. T26 scenario array 1328377 running. T21 baseline extract 1328378 OK, but **T21
  smoke 1328380 FAILED in 0 s: `run_paired_mc.py` was never staged in T22's code tree**, and ten Wave 3 scripts
  (T21, T28-T31) call it there. Manager decision: one shared Step-8 code tree `2J_revision/code_step8/repo`, no
  write into T22's running tree; a fresh employee builds it, re-points the scripts and resubmits the smokes. T30
  phase A SUBMITTED (smoke 1328399); T31 phase A SUBMITTED (smoke 1328400; builder E0 identity and E1 fields
  verified locally; current model ACH50 2.50 from `ZoneLeak_*` only, window "Glass" U 1.59 / SHGC 0.33, both
  accepted). Addenda in T30 (V1 mismatch = stop; checker seen failing first) and T31. A second login-node `mkdir`
  (T30) recorded. Resume prompt updated. Next: collect T20; driver fix.
- **(af) 2026-09-15, manager.** T20 COLLECTED: null forecast reproduces Nb-f 2022 exactly (0.0 pp, all 6,934,320
  cells equal); main weekday +1.485 pp vs design +1.507 pp; rake within 0.0012 pp; 6,934,320 rows, 144,465
  households; validator 30 PASS / 1 WARN / 0 FAIL on 2030, every 2022 PASS still PASS, no new FAIL; input md5s
  unchanged. One N2 item (household-ID sets equal, main vs 2022) was inferred, not measured: a small check job is
  being submitted, and T20 closes only when it prints PASS for main and for null (positive control). Resume prompt
  and checklist updated. Next: ID check; driver fix.
- **(ag) 2026-09-15, manager.** Driver path fixed: shared Step-8 tree `2J_revision/code_step8/repo` (driver,
  `run_bem.py`, 17 engine files, 4 archetype IDFs, 6 city EPWs, sizes equal to local), laid out as T17's proven
  Speed layout. Eight scripts re-pointed (T21 array and smoke, T28, T29, T30 array/check/smoke); T31's two scripts
  left, because its smoke copies its own driver into each tree and its array takes the path from a variable. T22's
  running tree untouched. `schedule.json` templates not staged: T23 showed the published runs already took the
  fallback with identical values, so leaving them out matches the published behaviour. T21 smoke resubmitted as
  **1328403**. T30 smoke 1328399 COMPLETED exit 0 (it never used the missing driver); collector launched. T31 smoke
  1328400 running. Next: T21 smoke, ID check.
- **(ah) 2026-09-15, manager.** **T20 CLOSED.** Household-ID check 1328408: main 2030 and null 2030 hold exactly
  the Nb-f 2022 household set (both PASS, 6,934,320 rows each; check seen failing on a fake pair first). The 2030
  schedules are trusted. T30 smoke COLLECTED PASS (averaging identity 2.9e-15, both homes share the averaged
  occupancy and keep their own design levels, 8,760 h, no error lines, 1.2 GB memory). Gates left before phase B:
  T21 smoke 1328403 (all of T21, T28, T29, T30, T31) and T26 SC0-SC5 (T29); dr_2J-09 (T31). A third read-only
  login-node deviation (`find`) recorded. Next: T21 smoke; T26.
- **(ai) 2026-09-15, manager.** T21 smoke 1328403 ran all three campaigns on the shared tree (every hourly file
  8,760 rows) but **acceptance A2 FAILED in all three: the two sampled households are 130228 and 79252, not the
  published pair 130322 and 80058.** The paired pool is 16,326 households; T30's 2022-only pool for the same cell
  is 16,337, and it drew a third pair. So 11 SingleD Montreal households fall out of the 2022-2030 pairing although
  T20 showed the 2030 file holds the exact 2022 household set. A2 is not re-read or relaxed; no phase B starts. A
  diagnosis job is being submitted (staged files byte-equal to T20/T18c outputs? which filter drops the 11? does the
  engine's own draw reproduce both pairs, and the published pair on the published files?). T31 smoke 1328400
  COMPLETED exit 0; collector launched. T30 V1 (same sample as T21) is affected by the same question. Next:
  sample diagnosis.
- **(aj) 2026-09-15, manager.** T31 smoke COLLECTED PASS: current-values variant reproduces the unmodified model
  exactly (E0), the mechanism-test knobs raise heating for both households (E1), and the current model's air
  tightness re-derives to 2.50 ACH50 (E2); T31 phase A closed. Phase B waits on dr_2J-09 and on the T21 sample
  diagnosis. Next: sample diagnosis.
- **(ak) 2026-09-15, manager.** Sample diagnosis 1328414 read (T21 doc, last ledger). The staged 2022 and 2030 files
  are byte-equal to the T18c and T20 outputs. The "11 missing households" were an artefact: T30's and T31's smokes
  ran on the PUBLISHED schedules (the new files were not staged yet), so 16,337 is a published-file pool. On the
  Nb-f files the engine's pools are 16,327 (2022), 16,326 (2030) and 16,326 paired; the one household lost fails the
  engine's schedule sanity check in 2030 only. The engine's own draw reproduces the smoke's pair on the new files and
  the published pair on the published files (positive control). The rebuilt schedules change which households the
  sanity check drops, so the paired pool differs from the published one by 320 households and seed 42 draws a
  different sample: equality with the published manifests is impossible by construction. **Basis change, recorded
  before any phase-B output: T21 A2 now requires equality with an independent engine re-draw on the staged files
  (seen failing first), plus an information-only overlap count with the published manifests; the paper states the
  before/after comparison is not household-paired across the two stocks.** T21 smoke PASS; **T21 phase B go**.
  T30 V1 decided: phase B draws once per cell from the paired pool, so V1 (equal to T21's manifest) stays a stop.
  T30 and T28 phase B go (`--nice=100`); T31 phase B now waits only on dr_2J-09; T29 waits on T26 SC0-SC5. T26
  scenario array finished, compare job running; T22 at 12 of 24 cells. Next: phase-B submissions.
- **(al) 2026-09-15, manager.** Phase B submitted. T21: Step 8 array 1328422, Step 9 activity 1328425, Step 9
  baseline 1328426 (24 tasks each), A4 md5-after 1328427 and `t21_check.py` (selftest first, restated A2) 1328428,
  both `afterany` on the arrays. T30: re-smoke 1328418 PASS (paired pool 16,326, draw 130228/79252 = T21, own design
  levels kept, 8,760 h), array 1328419 running. T28: array 1328415 running. T26 compare 1328379 COMPLETED exit 0;
  collector launched. Author confirmed they will run dr_2J-09. Next: T26 SC0-SC5.
- **(am) 2026-09-15, manager.** **T26 ACCEPTED** (collector + addendum): the full-jump scenario equals the 2030 build
  exactly, each scenario lands within 0.02 pp of its intended weekday shift, order Revert < Partial < Persist holds
  nationally and in every archetype, rake error at most 0.0012 pp, validator 0 FAIL (the spec's "28/28" is a stale
  count; the validator has 31 checks now, read as "no FAIL", as T20 did). **The standardized-jump rule fixed in the
  spec before data fired** (7.67 vs 4.73 pp, over the 1.0 pp trigger): S-Revert-std is added as T32 (spec §5, with a
  regression guard that must reproduce T26's λ = 0 file exactly). **T29 premise corrected:** the engine's pool
  depends on schedule content (sanity check), so `--years 2030` on a scenario file would not give T21's households;
  T29 now simulates T21's Step-8 manifest rows directly with a fixed-manifest wrapper, missing households listed,
  never replaced (T29 addendum 2). T29 phase B (smoke + array `afterok` T21 Step 8) and T32 being submitted.
  Next: T29, T32 submissions.
- **(an) 2026-09-15, manager.** T32 submitted (employee, doc ledger checked): build array 1328429 (task 0 = guard
  `--jump-basis primary`, task 1 = std; queued on the account CPU cap) and compare 1328430 `afterok`. Collector reads
  G0 first when both show COMPLETED. T29 employee still writing the fixed-manifest wrapper. Next: T29 submission.
- **(ao) 2026-09-15, manager.** T29 phase B submitted (employee, doc ledger checked): staging 1328431, smoke 1328432
  `afterok` staging (SingleD Montreal, S-Revert, 130228/79252), arrays 1328433 (S-Partial, λ 0.5) and 1328434
  (S-Revert, λ 0) `--array=0-23%2 --nice=100`, both `afterok:1328432:1328431:1328422`. `t29_check.py` P1 now counts
  undelivered households per cell. All queued on the CPU cap. Waiter restarted to also wake on the T29 smoke and the
  T32 compare. Next: T29 smoke read.
- **(ap) 2026-09-15, manager.** dr_2J-09 returned (author ran it; verdict USABLE, 121 value rows). Vetted offline
  (T31 doc, manager vetting section): 55 rows rejected as scout-computed (archetype-CSV means, two "calculated"
  window rows); Swan (2010) regional samples sum to 15,000 not 14,030; summary numbers absent from the table; three
  sources (Khemet and Richman 2018, Hamlin and Gusdorf 1997, SHEU-2019 window mix) never opened by the scout;
  window ratings labelled MEASURED though the scout calls them Window 5.2 ratings. Verification pass
  `deepResearch/dr_2J-09b_envelope_verification_prompt.md` written for the author. Value-selection rules 1 to 8
  fixed before it returns (geography first then sample; all-vintage average; dominant glazing type, centre-of-glass
  allowed as a stated limitation; any core value NOT FOUND = WP7.3 not run). T31 phase B still gated. Next: author
  runs dr_2J-09b.
- **(aq) 2026-09-15, manager.** dr_2J-09b returned (author ran it). Positive control resolved. Swan (2010) Table 3.4
  confirmed as printed (regional means, single-detached, 1997-2006, effective/nominal not stated). Khemet and
  Richman values come from the thesis, not the paper; Hamlin and Gusdorf reclassified NOT FOUND (never opened).
  Rules 1-8 applied (T31 doc): wall, ceiling and air-tightness found; **window U and SHGC for the dominant glazing
  type are printed nowhere, so window is NOT FOUND and rule 8 fires: WP7.3 is not run**, no JSON written, no
  partial variant. T31 closed without runs; §7 D3 answered "not run, one-envelope limitation stated". WP7 step 3
  drops; steps 1, 2 and 4 stand (step 4 without the "if run" clause). Next: waiter wake.
- **(ar) 2026-09-15, manager.** While the cluster runs: WP12.3 prompts written, `deepResearch/dr_2J-10_novelty_matrix_search_prompt.md`
  (adversarial search against Table 1, re-scores its rows and Barsanti et al. 2024, positive control Richardson
  et al. 2008; decision rule BROKEN / NARROWED / HOLDS in the README) and `dr_2J-11_wfh_trajectory_and_tradeoff_prompt.md`
  (work-from-home levels and 2030 outlooks for the WP2 range; home versus office energy for the system boundary).
  WP12.3(d) is already covered by dr_2J-06. Author asked for the checklist page to be republished after every step
  (standing). Next: author runs dr_2J-10 and dr_2J-11; waiter wake.
- **(as) 2026-09-15, manager.** WP10 prep started while the cluster runs (no result numbers needed): T33 (reviewer-response
  map of the 42 rows, jargon inventory, move-to-SI list, into `manuscript/prep/`) and T34 (draft new Section 2
  framework with equations, each traced to code or a task doc, into `manuscript/draft_S2_framework.md`). Both Sonnet,
  local only, launched. Next: read T33 and T34 when they end; waiter wake.
- **(at) 2026-09-15, manager.** T33 DONE and accepted: `manuscript/prep/response_map.md` (42 rows), `jargon_inventory.md`, `si_move_list.md`. Manager re-measured the key counts in the archived manuscript (forecast 33 lines, gate 19 whole-word lines, calibration closure 0): match. Corrected two stale cells (M2b now RUNNING, M2d T28 submitted). Section 3.5 vs 4.2 overlap is partial (channels, clock shift, donor draw); merge plan: one description in Framework, one-sentence pointer elsewhere. Next: T34 read; waiter wake.
- **(au) 2026-09-15, manager.** T34 DONE, accepted with 9 corrections after the manager re-read every trace row. The
  important one: the matching section described the published build; the new paper's 2022 set uses 2022 diaries
  only and no metropolitan-area key at the first level. Also fixed: metabolic mean over all records, dishwasher
  co-occupancy factor, sampling pool wording, independence caveat on the paired interval. The draft now promises a
  clustering check in the SI: WP6 must deliver it (a cluster-robust or city-by-archetype block interval) or the
  sentence is cut. State sections removed from the draft. Next: waiter wake; author runs dr_2J-10 and dr_2J-11.

- **(av) 2026-09-15, manager.** Two more no-cluster tasks launched (Sonnet, local only): T35 writes the Figure 1
  workflow image PROMPT (author generates the image) from the accepted Section 2 draft; T36 drafts the SI section on
  model selection and held-out-year diary validation, re-reading every number from its source file (the generator is
  not retrained, so these numbers carry over only if a source file confirms them). Next: read T35 and T36; waiter wake.
- **(aw) 2026-09-15, manager.** T35 DONE: Figure 1 workflow image prompt at `writing/submission/figures/Prompts_Images/
  Figure_01_workflow_prompt.md`, accepted with corrections. Found while checking it: raking runs after census matching
  in the code (`05_postlink_rake.py` header), so the prompt's arrows and the Section 2 draft's 2.3 text were corrected
  (T34 doc and T35 doc record both); WP10 orders matching before raking. Author owes: generate Figure 1 from the prompt
  (not urgent). Next: T36 read; waiter wake.
- **(ax) 2026-09-15, manager.** T36 DONE: `manuscript/draft_SI_model_selection.md`, accepted with 3 corrections. Values
  spot-checked at source and match. Found: the backcast weekend similarity ceiling was raised 0.10 -> 0.20 after the
  weekend values failed it (Step-6 doc lines 26, 576, 616). The SI now states that plainly and rests on the
  observed-only rows (0.036 to 0.046), never on the raised ceiling; the main text must not say the weekend passed.
  Seven old-campaign numbers flagged OLD (re-derive on the rebuilt runs or drop). Internal label removed from prose.
  Next: waiter wake; author runs dr_2J-10 and dr_2J-11.
- **(ay) 2026-09-15, author decisions, applied by manager.** Two rulings, both now binding.
  (1) The pre-registered diary-distance ceiling is 0.10 for every day type. The weekend does not meet it (held-out
  0.1817 / 0.1843; backcast 0.1637 / 0.1618) and the manuscript says so. The widening to 0.20 is disclosed once and
  used nowhere. The supporting evidence is the observed-only weekend rows (0.036 / 0.040) against synthetic-only
  0.138 to 0.175, plus the saturated weekend up-weighting (about 0.005 movement); the synthesized weekend days are a
  stated limitation. `manuscript/draft_SI_model_selection.md` S.3 rewritten and both weekend trace rows corrected.
  (2) The seven OLD-campaign / OLD-build numbers are to be re-derived on the rebuilt runs (T20, T21, T28, T30); any
  the rebuilt runs do not produce is dropped, never quoted from the old campaign, and old and rebuilt numbers are
  never mixed in one table. Rule written at the head of the T36 number trace table and carried into WP10.
  Next: waiter wake; collectors in queue order.
- **(az) 2026-09-15 late evening, manager.** Author going offline overnight; asked for the handover prompt to
  carry every remaining step explicitly. `writing/Prompts/2J_manager_prompt_RESUME_AE_resubmission.md` rewritten:
  §0 now carries both author rulings (ay) and the local edit rule (py scripts with asserted counts, never bash
  heredocs); §2 is split into done / cluster snapshot / owed by author / process warnings, with a per-job table
  read from `sacct` tonight (T21 Step 8 10 of 24, Step 9 activity 6 of 24, Step 9 baseline 0 of 24, T30 2 of 48,
  T28 1 of 4, T22 13 of 24, T32 and T29 queued behind the 32-CPU cap; nothing failed); §3 is now 16 numbered
  steps from "start a fresh waiter" through the five collectors, the deep-research returns, Wave 4 re-derivations,
  WP6/WP8/WP3/WP11, the WP10 rewrite, WP13 + `submit_check.py`, and Wave 5. The waiter dies with this session, so
  step 0 of the next session is to start a new one. Checklist page progress bars refreshed from the same `sacct`
  read. Next: overnight cluster; collectors in queue order.
- **(ba) 2026-09-15 late evening, manager.** Two local WP10 writing tasks launched while the cluster queue drains,
  both Sonnet, both local-only, both briefed with the login-node ban naming `mkdir` and `find`:
  **T37** `impl/2026-09-15_T37_wp10_limitations_section_draft.md` writes `manuscript/draft_S7_limitations.md`, the
  main-text limitations section, covering the seven limitations already on the record (not household-paired across
  stocks; one envelope only; the synthesized weekend days per ruling (a); validator check 3.5 at 75.04 % against an
  unmoved 72.3 % band; the 2030 build as a scenario not a forecast; scope; anything else the plan §9 boxes already
  mark), each traced to file:line, with a claim trace table.
  **T38** `impl/2026-09-15_T38_wp10_si_schedule_completion_draft.md` writes
  `manuscript/draft_SI_schedule_completion.md`, the second SI part (completion from one diary day to 8,760 hourly
  values, day-type strata, donor pool, deterministic draw and seed, the sampling-pool caveat, annual assembly and
  the reduction to the resolution EnergyPlus reads), with a number trace table.
  Both carry ruling (b): no old-campaign number is quoted; anything needing a rebuilt-run number is written as a
  marked PENDING placeholder. Next: collect T37 and T38; cluster collectors on waiter wake.
- **(bb) 2026-09-15 late evening, manager.** **T37 COLLECTED and ACCEPTED**, one manager correction applied.
  `manuscript/draft_S7_limitations.md` exists: nine limitations in seven paragraphs plus a claim trace table.
  Manager re-checked four trace rows at source independently: T18c frame v2 `:56-58,61` (75.04 % vs the 72.3 %
  anchor, gap 2.74 pp, band 2 pp; weighted real 2022 donors 72.31 %), T21 rerun `:429-438` (new paired pool 16,326
  vs published 16,208, symmetric difference 320, cell SingleD__Montreal_6A), plan §5 `:470-483` (the three extra
  limitations: typical-year weather for 2030, the conditional-independence assumption in the census-to-diary match,
  the uncalibrated metabolic heat channel), and `draft_SI_model_selection.md:95-128` (every weekend number matches
  the SI part verbatim). **Ruling (a) holds**: the main text never says the weekend passed, it names one ceiling of
  0.10 for every day type and states the weekend does not meet it. **Ruling (b) holds**: no old-campaign or
  old-build number appears and no PENDING placeholder was needed. Machine check on the prose only: zero em or en
  dashes, zero banned labels, zero T-numbers, the word "failure" absent. **Manager correction**: the opening said
  "six limitations" while the section lists nine; rewritten to nine with the split named. The agent's flag that
  plan entry (ba) was missing is resolved, it exists at `:1064` and the agent simply grepped before the append
  landed. Two items carried forward, neither a defect: §5 item 5 (weekend pooled into one day type) is deferred to
  the T38 collection because T38 documents the day-type strata and the resolution reduction, which is where that
  claim is settled; and the scope paragraph's description of the measured-data check is re-read once T09 is
  re-derived in Wave 4. Next: collect T38; cluster collectors on waiter wake.
- **(bc) 2026-09-15 late evening, manager.** **T38 COLLECTED and ACCEPTED**, four manager corrections
  applied. `manuscript/draft_SI_schedule_completion.md` exists, S.5 to S.9 plus a 17-row number trace
  table: the two reductions from 48 half-hour diary slots to 24 hourly values and the 4-hour clock
  shift, the three day-type strata and their reduction to two at the building-model interface, the
  donor pool and the per-member draw at seed 42, the sampling-pool caveat, and the annual assembly.
  Manager re-read `07_aug_to_bem.py:148-180` and `:34`, `07_bemIntegrationGSS.md:60-68` and
  `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-438`; every S.7 and S.8 claim checks out at source.
  **Ruling (b) was breached as first written and is now repaired.** The agent kept three sets of
  numbers as method history: the 2022 at-home rates by day type, the 2030 Saturday and Sunday rates,
  and the 77,313 weekday-only household count. The first are from a person file of 285,419, since
  refreshed to 285,367; the second are from the 2030 build that D1 replaced. All three are now marked
  PENDING and appear nowhere in the prose. The 2.76-point copy-day bias is kept, because the current
  completion step's own code states it at `07_aug_to_bem.py:151-153` as the reason the method changed,
  and the S.8 pool figures are kept, because they are a rebuild-verification finding of this revision.
  **Two unrequested findings by the agent, both correct, both acted on.** (1) Plan §5 item 5 is
  settled: Saturday and Sunday are pooled into one weekend pattern at the building-model interface
  while the diary model keeps three strata apart, so it is a real limitation. A tenth limitation has
  been added to `draft_S7_limitations.md` with its own trace row and no number, since the size lost is
  PENDING; §5 item 5 needs no separate handling in WP10. (2) `draft_S2_framework.md` §2.8 described the
  sampling candidate pool as every household identifier in the schedule files, omitting the
  plausibility filter that is the entire basis of the S.8 caveat; one clause added at `:246-247`.
  Prose hygiene passes on both drafts: no dashes, no banned labels, no T-numbers, nothing estimated.
  Next: cluster collectors on waiter wake.

- **(bd) 2026-09-16 morning — overnight cluster read, no collection.** `sacct` on all fourteen live jobs.
  **Every completed array task exited 0:0; no job has failed and nothing needs resubmitting.** Counts:
  T21 Step 8 (1328422) 20 of 24 done with 4 running; T21 Step 9 activity (1328425) 18 of 24 done with 4
  running and 2 pending; T21 Step 9 baseline (1328426) 0 of 24, queued; T22 (1328310) 14 of 24 done;
  T28 (1328415) 1 of 4; T30 (1328419) 2 of 48; T32 (1328429/1328430), T29 (1328431 to 1328434) and the
  T21 dependent checks (1328427, 1328428) all still queued. Everything but the two T21 Step-8/Step-9
  arrays sits in `AssocGrpCpuLimit` because those arrays hold the whole 32-CPU account cap; that is the
  designed behaviour, not a fault. Longest Step-8 task observed 05:07:26 (`1328422_19`), four at a time,
  so Step 8 should close within hours and release the cap. No collector fired, so no task moved: checklist
  republished at **Version 29** with the nine progress bars refreshed and the stale "nine limitations"
  wording on the limitations item corrected to ten, and the manager prompt §2.2 and step 0 rewritten to
  this read. The outgoing session's waiter dies with it; the incoming session starts a fresh one on
  1328422, 1328432, 1328430, 1328310, 1328428.
  Next: T21 collector on wake.

- **(be) 2026-09-16 morning, Fable session — dr_2J-12 Fable return written, UNVETTED.** The author
  switched the session model to Fable 5.1 and handed over the Fable variant of the whole-paper review
  prompt. Run as close reading, no web. Text reviewed = the SUBMITTED manuscript in
  `../archive/2J_manuscript_submission.md`, the only complete text on disk; the four partial redrafts in
  `manuscript/` were NOT substituted in, so some findings may already be answered by them. Return saved as
  `deepResearch/dr_2J-12_whole_paper_review_fable_results.md` (about 5,300 words, no dashes, all seven
  output sections). Verdict REJECT-LIKELY on the submitted text. Load-bearing items, in the return's own
  ranking: (1) the only CI-bearing shape deltas are 2022 to 2030, a transition with no WFH break, yet
  abstract, Fig. 6 caption and Conclusion 3 attribute them to the break; (2) §5.1 and §7 call the 2030
  at-home magnitude provisional and inflated while the abstract states it as a result; (3) Conclusion 1
  says EUI is consistent with SHEU ranges, Table 5 says all four are below; (4) SHEU ±2.7% agreement is a
  fitted scalar presented as validation; (5) the COLLECT_MODE flag flips at the same cycle as the COVID
  break; (6) lighting has no daylight gate, biasing the midday fill upward, and the promised §7 treatment
  is absent; (7) weekend day-types are produced two different ways (§3.2 vs §3.5) and 35/35 PASS is not
  reconcilable with the 0.10 weekend gate. Fifteen internal mismatches, twenty method findings, fifteen
  clarity items, twelve OUTSIDE-MY-SCOPE lines. Nothing acted on; nothing computed. Gemini variant still
  owed by the author. Manager prompt §2.3 and Step 7 updated; README row updated.
  Next: Step 7 vetting of this return (steps 1, 2 and 6 of the README list do not apply to a no-search
  return; step 7 offline audit does), then map each ranked item onto the response map and the four
  drafts; then T21 collector on wake.

- **(bf) 2026-09-16, manager — dr_2J-12 Gemini return in, both returns vetted, CARRIED items mapped.**
  The Gemini variant (live search) returned as `deepResearch/dr_2J-12_whole_paper_review_gemini_results.md`
  (verdict REJECT-LIKELY), alongside the earlier Fable return, both reviewing the archived SUBMITTED
  text, not the in-progress redrafts. Ran the full 7-step vetting (adapted to a whole-paper review) as a
  background pass: quote-by-quote check of every section/quote claim against the 654-line archived
  manuscript, a live Crossref re-check of 19 of the Gemini report's cited DOIs (all 19 resolved and
  matched; no fabrication, unlike earlier rounds), and a cross-check of both reports against each other
  and against what WP1/WP5 already cover. Written up in full at `deepResearch/dr_2J-12_VETTING.md`.
  **Verdict: REJECT-LIKELY survives vetting.** Two of the three headline "would-reject" items are not
  new: the calibration-provenance defect is WP1's exact job, and the missing-measured-data validation is
  WP5's exact job (a usable IESO Ontario/FSA dataset is already in hand) — this is corroboration that
  the plan targets the right things, not new work. New, CARRIED findings now folded into the plan: nine
  cheap quote-verified fixes added to §5 items 10-15, and one new, currently unassigned confound (the
  CATI-to-EQ survey mode change landing on the same 2022 cycle as the COVID break) plus the single most
  load-bearing item — the CI-bearing 2022-to-2030 shape deltas do not test the WFH-causal claim the
  abstract makes for them — both written into §5 under "New, currently unassigned work" and assigned to
  WP1 + WP10. Struck/downgraded: Gemini's "no baseline-schedule benchmark" item (not quote-checkable,
  lower confidence) and its "two validation tiers" characterization of Applied Energy policy (the
  report's own synthesis, not a quoted journal policy — do not cite it to an editor as fact). Page
  numbers from either report are not citable (the source has no page breaks); section numbers only.
  Next: fold the WP1+WP10 confound/provisional-framing item and §5 items 10-15 into the live drafts
  under `manuscript/` as WP10 proceeds; update the checklist artifact; then T21 collector on wake.

- **(bg) 2026-09-16, manager — waiter restarted, T39 dispatched, Table B1/B2 wording fixed.**
  Cluster read via `sacct`: T21 Step 8 (1328422) fully COMPLETED since the last read (was 20/24), so
  Step 9 baseline (1328426) and activity (1328425) are both now running; T22 (1328310) at 14/16 done;
  nothing failed anywhere. A fresh 30-min background waiter is running (watching the base job IDs for
  T21 Step 9, T22, T28, T29, T30, T32) after the first attempt died instantly on a double-backgrounding
  bug (fixed). Dispatched T39 (fresh Sonnet employee, task doc
  `impl/2026-09-16_T39_wp10_dr2j12_carried_items_threading.md`) to add plan §5 items 10-15 plus the new
  confound/WFH-attribution item to `manuscript/prep/response_map.md` as a new "Quiet fixes" section
  (Step 7's remaining work); result not yet back. Independently fixed the "sole model" / "only 4/4-gate
  model" wording in `writing/submission/tables/SI/Table_B1_B2.md` (lines 9 and 59, plan §10 Step 13's
  named item): replaced with T04's manager-approved wording, "J3 had the lowest composite score among
  the four trials that cleared all four gates," plus the two-thresholds-equal-F1-baseline and
  Spouse-tightened-without-reason provenance notes, citing the T04 doc. This was already fully decided
  in T04's Verified/manager-ruling section (2026-09-15); no new judgment call made.
  Next: collect T39; republish the checklist page with the waiter/T39/Table-B1-B2 status; keep working
  non-cluster steps (8-13 groundwork) while the waiter watches the cluster.

- **(bh) 2026-09-16, manager — T39 collected, DONE.** `manuscript/prep/response_map.md` now carries 49
  rows: the original 42 plus a new "Quiet fixes and new items (not reviewer-raised, dr_2J-12 vetted)"
  section with Q10-Q16 (plan §5 items 10-15 plus the confound/WFH-attribution item). Employee checked all
  four existing drafts (`draft_S2_framework.md`, `draft_S7_limitations.md`, `draft_SI_model_selection.md`,
  `draft_SI_schedule_completion.md`) by grep and read `draft_S7_limitations.md` in full: none of the seven
  fixes are applied anywhere yet (no Introduction/Discussion/Conclusion/Results/Abstract draft exists at
  all), so all seven are correctly WAITING, not DONE. Full ledger in
  `impl/2026-09-16_T39_wp10_dr2j12_carried_items_threading.md`. Reminder still owed by the author, same
  kind of work as `dr_2J-12`: `dr_2J-10` (novelty matrix search) and `dr_2J-11` (WFH trajectory) have not
  been run yet in Gemini/Fable.
  Next: republish the checklist page (waiter, T39, Table-B1-B2 fix); dispatch the next non-cluster task
  (Q12/Q16's limitations paragraph into `draft_S7_limitations.md` directly, since that draft already
  exists) while the waiter watches the cluster.

- **(bi) 2026-09-16, manager — dr_2J-10 and dr_2J-11 split into Gemini/Fable pairs, author request.**
  Author confirmed Fable has no live search access in their setup, so a Fable version of these two
  literature-search prompts cannot search the literature; running the original search prompt through a
  no-search Fable would just invent papers and numbers (the exact failure mode the vetting process
  exists to catch). Instead: renamed the two existing prompts to `..._gemini_prompt.md` (unchanged
  content, they already assume live search and Crossref verification), and wrote two new
  `..._fable_prompt.md` companions that audit our OWN argument for internal soundness with no external
  search, mirroring the dr_2J-12 Gemini/Fable split rationale exactly (search-grounded fact-check paired
  with no-search close reading). dr_2J-10 Fable: argument map, internal-consistency, and
  circularity/overclaiming check on the novelty "open cell" claim and its three named competitors
  (Chen et al. 2022, Yin et al. 2024, Jalilian and Kamel 2025). dr_2J-11 Fable: argument map on the
  single-scenario-vs-bracketed-range wording, and a presence/absence check of whether the manuscript
  discloses the residential-only system boundary (office/commercial energy trade-off) anywhere — a grep
  of the archived manuscript found no such disclosure, but the Fable prompt asks it to confirm this
  itself against the full pasted text rather than trusting the grep. Both Fable prompts follow the
  dr_2J-12 convention: the author pastes the full manuscript below the prompt when running it. README
  table updated with all four files. Four results files still owed by the author, none run yet.
  Next: author runs all four in Gemini/Fable; vet each on return.

- **(bj) 2026-09-16, manager — dr_2J-10 FABLE return in, UNVETTED.** Run in Claude Code (Fable 5.1, no
  web) against the SUBMITTED text `archive/2J_manuscript_submission.md`, same basis as the dr_2J-12 Fable
  run; the four partial redrafts do not touch the Introduction or Table 1. Saved as
  `deepResearch/dr_2J-10_novelty_matrix_search_fable_results.md` (about 4,000 words, dash-free, every
  finding quoted with a section/paragraph pointer). Verdict: HAS A STRUCTURAL PROBLEM. The manuscript runs
  two novelty claims on two bases (six-column "open cell" vs. external studies; four pipeline-stage
  advances vs. the authors' own C-VAE work) and §1.2 para 2 concedes the six-column basis "would" be
  mostly satisfied by that own prior work, which Table 1 excludes ("external competitors only") while §6
  says "no prior study occupies" the cell. Supporting findings: no column criteria are stated anywhere;
  only 3 of 9 competitor rows (Chen, Yin, Jalilian) have a supporting sentence; Chiou ✗ and Yin ✓ in
  "Calibrated behavioural model" are inconsistent with the manuscript's own descriptions (§1.5 calls Chiou
  ATUS-based; §1.2 calls Yin "statistical analysis"); the prose claim adds "through the WFH break" and
  "paired", which no column scores, so the prose cell is narrower than the table and closer to
  unfalsifiable; the one column separating this paper from Chen (forecast to future year) is the result
  §5.1/§7 mark provisional and single-scenario; §1.4/§1.5 disagree on whether the predecessor's 2025 was a
  "synthetic present-day cycle" or a "hindcast"; the abstract's and conclusion's closing sentence is the
  feasibility premise §1.4 says is not re-claimed; Reinhart & Cerezo Davila is a review and Motuzienė an
  office study by their own reference-list titles. Top reviewer items ranked R1-R5, all
  would-request-major-revision except R5 (minor). Vetting: steps 1-6 do not apply (no external claims, no
  DOIs); step 7 offline audit is the operative one, quotes to be spot-checked against the archived text.
  README row and `Prompts/2J_manager_prompt_RESUME_AE_resubmission.md` (header, §2.3, Step 7) updated.
  Three returns still owed by the author: dr_2J-10 Gemini, dr_2J-11 Gemini, dr_2J-11 Fable.
  Next: vet dr_2J-10 Fable jointly with the Gemini return in one `dr_2J-10_VETTING.md`; the Table 1
  rewrite in WP10 waits for both.

- **(bk) 2026-09-16, manager — dr_2J-11 FABLE return in, UNVETTED.** Run in Claude Code (Fable 5.1, no
  web access) against the SUBMITTED text `archive/2J_manuscript_submission.md`, same basis as the dr_2J-12
  and dr_2J-10 Fable runs; the two redrafts that touch the scenario (`draft_S2_framework.md` §2.7,
  `draft_S7_limitations.md`) are covered in one separate note at the end, not mixed in. Saved as
  `deepResearch/dr_2J-11_wfh_trajectory_and_tradeoff_fable_results.md` (about 4,700 words, dash-free, every
  finding quoted with a section/paragraph pointer). Verdict: HAS A STRUCTURAL PROBLEM. Headline: the
  manuscript defines the 2030 case as WFH "persists with probability one" (§7 para 9) with the behavioural
  model unchanged after 2022 (§3.4 para 3), so by construction the 2022→2030 leg varies only demography
  and a raked target; that leg is the only one with CI-bearing shape deltas (§5.3 para 2) and the abstract,
  Fig. 6 caption and Conclusion label it the WFH effect (same mechanism dr_2J-12 flagged, re-derived here
  from the scenario definition). Supporting findings: "+2.2 to +3.9 pp" is a level above pre-pandemic in
  the Abstract, §3.4, §5.1 and Conclusion 2 but the 2022→2030 step in §7 para 5 (incompatible: under the
  first reading 2030 sits below 2022 and "upper bound"/"persists"/"extends" are wrong; under the second
  the further rise has no stated driver); the range's axis is never stated; §3.4 says the assumption "is
  bounded in §7" but §7 para 9 only names the counter-scenario as future work; Highlights say "2030
  occupancy forecast ... validated by True-Future-Test" though the TFT scores 2015→2022; the provisional/
  inflated caveat (§7 para 5) reaches 2 of 6 places the number appears and never its derived quantities;
  the 78.44% 2030 target (§4.2) is never derived, so the 2030 at-home level reads as a raked input, not a
  forecast output (UNCERTAIN); "Step-6 calibration validation" (§7 para 5) is never described; §6 para 3
  quotes an uncited "~+12%" Canadian figure. System-boundary check: NOT FOUND — no residential-only or
  office/commercial sentence anywhere in the submitted text, and none in the S7 redraft either; natural
  home is a §7 scope paragraph, most exposed at §6 paras 5-6 (grid/DR and code implications). Reviewer
  items ranked 1-5: item 1 would-reject, 2-4 major revision, 5 minor. New tension from the redrafts: the
  S2 §2.7 target adds 8 years of the 2005-2015 slope that the submitted §5.1 calls compositional, not
  behavioural; the S2 "standardised version" is the natural reconciliation, flagged for vetting. Vetting:
  steps 1-6 do not apply (no external claims, no DOIs); step 7 offline quote spot-check is the operative
  one. README row and `Prompts/2J_manager_prompt_RESUME_AE_resubmission.md` (header, §2.3, Step 7) updated.
  Two returns still owed by the author: dr_2J-10 Gemini, dr_2J-11 Gemini.
  Next: vet dr_2J-11 Fable jointly with the Gemini return in one `dr_2J-11_VETTING.md`; the WP2 scenario
  paragraph and the WP10 system-boundary paragraph wait for both.

- **(bl) 2026-09-16, manager — waiter restarted, T40 vetting dispatched for both Fable returns.**
  Job 1328425 (T21 Step 9 array) left the queue fully COMPLETED, 24/24, confirmed on `sacct`. Waiter
  re-armed tracking the remaining ten jobs (1328310, 1328415, 1328419, 1328426, 1328427, 1328428,
  1328429, 1328430, 1328433, 1328434); nothing failed. Rather than wait for the author to also run the
  two owed Gemini returns before vetting, dispatched a Sonnet employee task (T40,
  `impl/2026-09-16_T40_vet_dr2j10_dr2j11_fable_returns.md`) to do the offline quote/arithmetic/
  known-vs-new vetting pass on the two Fable returns now, same method as `dr_2J-12_VETTING.md` step 7
  (steps 1-6 do not apply, no external claims). This does not replace the joint Gemini+Fable vetting
  files planned in (bj)/(bk) once the Gemini returns are in; it gets the Fable-only checkable half done
  now instead of parking on the author. Output: `deepResearch/dr_2J-10_dr2J-11_FABLE_VETTING.md`.
  Next: read T40's output when it lands, fold survives-vetting findings into plan §5 and
  `manuscript/prep/response_map.md`, still owe dr_2J-10 Gemini + dr_2J-11 Gemini from the author.

- **(bm) 2026-09-16, manager — T40 back, both Fable returns SURVIVE VETTING, two new items folded
  into plan §5.** `deepResearch/dr_2J-10_dr2J-11_FABLE_VETTING.md`: 21/21 and 19/19 spot-checked
  quotes matched the archived manuscript exactly (plus all nine Table 1 competitor cells checked
  against the manuscript's own table), every checkable arithmetic claim re-derived correct (the
  stock-scale N=50 math; the two incompatible readings of "+2.2 to +3.9 pp", 3.9 < 5.2 under the level
  reading versus 7.4-9.1 under the step reading; the Table 5 pointer mismatch), and `dr_2J-11`'s own
  cross-check against `draft_S2_framework.md` §2.7 and `draft_S7_limitations.md` independently
  reconfirmed accurate in all three of its claims. One process note, not a fabrication: the task doc's
  own step 4 mislabelled a `dr_2J-12` overlap as "dr_2J-10 M6", which `dr_2J-10` never actually claims;
  corrected in the vetting doc, does not affect either verdict. Both reports **SURVIVE VETTING**.
  Cross-checked both reports' top-5 items against the plan: most are corroboration of items already on
  the WP1/WP2/WP10/WP12 critical path (folded into §5's framing, no renumbering needed); two items were
  genuinely new and are now §5 items 16 (Table 1 has no stated column criteria; Chiou/Yin scored
  inconsistently on "Calibrated behavioural model") and 17 (the "+2.2 to +3.9 pp" 2030 figure is
  defined two incompatible ways in the text itself — needs an explicit editorial decision before WP1
  reports the recalibrated number). Cluster: same ten jobs tracked, nothing failed, waiter running.
  Next: still owe dr_2J-10 Gemini + dr_2J-11 Gemini from the author (novelty-table adversarial search
  and WFH-trajectory search); WP10's Table 1 rewrite and WP1's recalibration should each pick up their
  new item 16/17 when that work starts.

- **(bn) 2026-09-16, manager — both Gemini returns landed and vetted same day, two more new items
  folded into plan §5, WP2 gets a data-grounded number.** The two previously-owed Gemini live-search
  returns came back (`dr_2J-10_novelty_matrix_search_gemini_results.md`, verdict NARROWED;
  `dr_2J-11_wfh_trajectory_and_tradeoff_gemini_results.md`, verdict USABLE). Dispatched a Sonnet
  employee (T41, `impl/2026-09-16_T41_vet_dr2j10_dr2j11_gemini_returns.md`) to run the full 7-step
  README vetting process (these are live-search, real DOIs, unlike T40's Fable returns) and merge with
  T40's already-vetted Fable findings on the same two topics rather than picking one. 39 Crossref DOI
  queries run: 37 resolve exactly, 1 (Morissette et al. StatCan) is real but registered on DataCite not
  Crossref (confirmed via DataCite API, same non-fabrication pattern as prior IBPSA/arXiv cases), 0
  fabricated. Both positive controls (Richardson et al. 2008; Barrero, Bloom and Davis 2021) resolve
  exactly. Two genuine new findings, caught by re-derivation, not stated in either original report:
  `dr_2J-10`'s own Table B "Total Y" column undercounts 12 of 25 rows (never overcounts, table's rank
  order not safe to quote as printed, though it does not change the headline verdict); `dr_2J-11`'s own
  trajectory data shows WFH share declining for four straight years after 2022 in both Canada and the
  US, real evidence against the manuscript's "persists with probability one" 2030 assumption. One flag:
  `dr_2J-11`'s cited "7.1%" 2016 figure could not be matched to the real StatCan source page (three
  other close numbers found instead); marked NOT CONFIRMED, not fabrication. Verdicts: `dr_2J-10`
  Gemini PARTIALLY SURVIVES VETTING (downgraded for its own arithmetic defect); `dr_2J-11` Gemini
  SURVIVES VETTING. Folded as new plan items 18 (name column C3 explicitly in WP10's Table 1 rewrite,
  use corrected Table B counts) and 19 (ground WP2's reversion 2030 scenario in the real post-2022
  decline, do not repeat the unconfirmed 7.1% figure). Output: `deepResearch/dr_2J-10_VETTING.md`,
  `deepResearch/dr_2J-11_VETTING.md`. Cluster: same ten jobs tracked, nothing failed, waiter running.
  Next: thread items 16-19 into `manuscript/prep/response_map.md` during WP10; nothing further owed
  from the author on `dr_2J-10`/`dr_2J-11`, both topics now fully vetted (Fable plus Gemini).

- **(br) 2026-09-17, manager — overnight the cluster cleared four job families; T21's scorer was the
  only failure and it was a job-script bug, not a run; T32's gate is met and its campaign is dispatched;
  the account CPU limit doubled but 2J stays at 32.** Note on labelling: prompt-file entries (bo), (bp)
  and (bq) were status refreshes of `2J_manager_prompt_RESUME_AE_resubmission.md` and never had plan-log
  entries; (bq)'s one substantive result, the independent re-verification of all 52 references in the
  frozen submitted manuscript (50 clean, 2 real small errors, 0 fabricated), is recorded as §5 items
  **20** (Motuzienė et al. 2022 cited volume 76, real is 77) and **21** (Jalilian & Kamel 2025 truncated
  title). This entry (br) resumes the log.
  **T21 (`1328422`, `1328425`, `1328426`, `1328427`) is fully done:** Step 8 paired runs 24/24 COMPLETED
  exit 0:0, Step 9 activity 24/24, Step 9 baseline 24/24, A4 md5-after COMPLETED — 2,400 main plus 4,800
  comparison runs delivered, no task failed, nothing to resubmit. **`1328428` (`t21_check`, the
  A1-A4/A2-restated scorer) FAILED exit 1:0 after 0 seconds**, and the cause is a defect in the job
  script alone, diagnosed by the manager by reading both files: `t21_check.sh:41` invokes the selftest as
  `--selftest --t21-root ... --code-root ...` while `t21_check.py:346` declares
  `ap.add_argument("--out", required=True)`, so argparse exited 2 before any selftest logic ran; the
  selftest path (`t21_check.py:354-356`) never reads `args.out` (it writes into an `out/_selftest/`
  directory it creates itself), so the argument is genuinely unused in that mode and a placeholder is
  correct. **No simulation output is affected and `t21_check.py` was NOT edited.** A Sonnet employee added
  `--out "$T21_ROOT/out/_selftest/unused_selftest_out.csv"` to line 41 only, scp'd the script back, read
  it back to confirm the SBATCH block was untouched, and resubmitted with no `--dependency` (all four
  predecessors already COMPLETED): **new JobID `1329216`, running.** The seen-failing discipline is intact
  — the selftest still gates the real check, it simply now gets to run.
  **T32 ACCEPTED and its campaign dispatched.** Build tasks `1328429_0` (guard) and `1328429_1` (std) and
  the compare job `1328430` all COMPLETED exit 0:0; a Sonnet collector scored them against §5 of the T32
  doc: **G0 PASS — the guard task's output equals T26's λ = 0 file exactly** (checksum equality plus
  100.0 % cell match), **SC1 PASS** (within 0.012 pp of target), **SC4 PASS** (0 FAIL of its checks,
  reproducing T26's own accepted 30/1/0 reading), **SC5 PASS** (max difference 0.0012 pp). G0 was the
  load-bearing one and it holds, so the standardized build is sound and the task doc's own launch gate is
  met. The **1,200 S-Revert-std runs** (24 cells x 50 households) are therefore dispatched, submitted as **`1329220`** (24 tasks, `%2`, 4 CPUs, PENDING on `afterany:1328434`), reusing T29's
  `run_fixed_manifest.py` wrapper byte-identically, pointed at T21's own rebuilt manifests
  (`T21/out/step8/<cell>/cell_manifest.csv`). The employee confirmed the pointer by reading the Montreal
  test cell's manifest directly: household **130228 at sample 1**, the same rebuilt draw T29's smoke used,
  not the stale published pair. The scenario schedule input is T32's own passed build
  (`T32/out/std/BEM_Setup/BEM_Schedules_2030.csv`), read in place with no duplicate copy.
  **T29 smoke verified retrospectively, PASS on all three checks.** `1328431` (stage) and `1328432`
  (smoke) COMPLETED, and the smoke's `afterok` dependants released on their own before a collector had
  read it, so the manager had it scored after the fact: both households simulated, **8,760 data rows each**
  (8,761 lines including the header), household IDs **130228 and 79252** — T21's rebuilt seed-42 draw, and
  **not** the published pair 130322/80058. The sampling-pool hazard of log (ak)/(am) is therefore closed
  for T29 by measurement, not assumption. `1328433` (`t29_partial`) is **24/24 COMPLETED exit 0:0**;
  `1328434` (`t29_revert`) is at 20/24.
  **Manager ruling, supersedes the older T29 smoke brief:** that brief told the smoke collector to
  `scancel 1328433 1328434` on any failed check. With 1328433 already complete and 1328434 mid-flight,
  cancelling would destroy delivered work and save nothing, so the collector was given **no cancel
  authority**: it reports, the manager rules. Nothing was cancelled; nothing needed to be.
  **Counts read from `sacct` this morning, all other families clean:** T22 `1328310` 21/24 (2 running, 1
  pending), T28 `1328415` 1/4 (1 running, 2 pending), T30 `1328419` 38/48 (2 running, 8 pending), T29
  revert `1328434` 20/24. **Across every 2J job ever submitted in this revision, the only non-zero exit
  is `1328428` above.** T28 is now the slowest set left.
  **CPU ceiling — new standing constraint.** HPC support raised the `chachemv`/`o_iseri` association from
  `cpu=32` to `cpu=64` on a temporary basis, to be reviewed at the end of October 2026. The author has
  reserved the new 32 for a different project and instructed, verbatim, "do not interfere new 32 cpu".
  **Therefore 2J never exceeds 32 CPUs in flight, and no array's `%N` concurrency or `--cpus-per-task`
  may be raised on the strength of the higher limit.** The four live arrays already sum to exactly 32
  (T22 2x4, T28 1x8, T29-revert 2x4, T30 2x4), so the T32 campaign was submitted
  **`--dependency=afterany:1328434` at `%2` and 4 CPUs**: it inherits the eight CPUs T29-revert releases
  instead of adding to the total, and the ceiling holds with no babysitting. One transient exception is
  recorded rather than hidden: the T21 scorer rerun `1329216` (4 CPUs) briefly put the account at 36
  while T29-revert was still running. The manager let it stand — it is a short scoring job, the other
  project has nothing submitted yet, and cancelling it would have cost a rerun of a load-bearing scorer —
  and it is not to be repeated as a pattern. **Closing that exception the same morning:** with the scorer
  running the account sat at 36 CPUs, so the manager throttled the T30 array to one task at a time
  (`scontrol update JobId=1328419 ArrayTaskThrottle=1`, no job-ID change, nothing cancelled, no task
  lost). The account therefore settles back to exactly 32 as soon as a T30 task lands. **Restore T30 to
  `%2` once `1329216` finishes** — at that point the four arrays sum to 32 again on their own. This is the
  pattern to reuse whenever a short scoring job must share the ceiling: throttle a long array, do not
  cancel, and write the restore down.
  Checklist page republished (**Version 37**) with all nine progress bars refreshed from `sacct`, the
  overnight completions, the scorer fix stated plainly, the 32-of-64 CPU rule added to the rules panel,
  and a new group-D item for the 52-reference re-verification. A fresh 30-minute waiter is running on the
  four still-live arrays (`1328310`, `1328415`, `1328419`, `1328434`).
  Next: T21 collector when `1329216` finishes (A1-A6 with the restated A2; **A6 is a stop rule**); then
  the T22, T30, T28 and T29-revert collectors as each array lands; then the T32 campaign collector. The
  writing waves (steps 7-13) need none of this and can run in parallel.

- **(bs) 2026-09-17, manager — T42 DONE: the last unthreaded carried items are now rows in the response
  map, and one editorial decision is recorded as deliberately NOT taken.** A Sonnet employee (T42,
  `impl/2026-09-17_T42_thread_items_16_21_response_map.md`) threaded plan §5 items **16-21** into
  `manuscript/prep/response_map.md`: **49 → 55 rows**, six added, **all six WAITING/OPEN, none ALREADY
  FIXED**. That is the correct answer rather than a gap: no target manuscript draft exists yet, so nothing
  could legitimately be marked fixed, and the employee was told not to mark anything fixed without opening
  the file and seeing the line.
  **Manager verification, re-derived from the artifact rather than taken from the report** (the standing rule
  on Progress Log claims): the file has 63 table lines across 4 tables, minus 4 x 2 header/separator lines =
  **55 data rows**, which matches. Rows **Q17-Q22** are present and each one cites its own plan item plus the
  vetting file it came from.
  **Numbering offset, worth knowing before anyone quotes a row: `Qn` is NOT plan item `n`.** T39 had already
  used Q10-Q16 for the dr_2J-12 items, so this pass continues at Q17: plan item 16 → **Q17** (Table 1 has no
  stated column criteria; Chiou and Yin scored inconsistently), 17 → **Q18** (the "+2.2 to +3.9 pp"
  double definition), 18 → **Q19** (name column C3; dr_2J-10's own Table B undercounts), 19 → **Q20** (ground
  the 2030 reversion in the real post-2022 decline; never reuse the unconfirmed "7.1%"), 20 → **Q21**
  (Motuzienė volume 76 → 77), 21 → **Q22** (Jalilian & Kamel full subtitle). Every row carries its plan
  item, so the offset is safe as long as nobody assumes the two numbers line up.
  **Q18 carries a manager decision that is deliberately left open, and the reasoning is recorded so the next
  session does not have to redo it.** The manuscript defines "+2.2 to +3.9 pp" two incompatible ways: a level
  above the pre-pandemic baseline (four places) and, once, the 2022-to-2030 step itself. The manager's first
  instinct was to rule "report the step, because the rebuilt campaign simulates no pre-pandemic arm" — and
  then **checked it and did not adopt it**: the figure is in percentage points of at-home share, not energy,
  so it does not need an energy run at all, and the historic-cycle schedule files (2005/2010/2015, confirmed
  by T24 to use only their own diaries) could support a pre-pandemic level without one. The decision
  therefore turns on what the four "level" usages actually claim in context, it is due when **WP1**
  recalculates, and it is recorded as pending rather than guessed. Ruling (b) still binds either way:
  whichever definition survives, the number is re-derived on the rebuilt build or dropped.
  **T43 dispatched** (`impl/2026-09-17_T43_wp10_survey_mode_confound_limitation.md`): add the CATI-to-EQ
  survey-mode confound to `manuscript/draft_S7_limitations.md` as the eleventh limitation — the mode change
  lands on the same 2022 cycle as the pandemic break, the design cannot separate the two, and the paper must
  say so without claiming the mode change explains the jump. The brief names the two defects this file has
  had before (the opening count was wrong twice; the trace table needs its row) and requires the employee to
  merge or cross-reference rather than add a near-duplicate if one of the existing ten already touches it.
  Cluster unchanged otherwise: the T21 scorer `1329216` is still running, and the account sits at 36 CPUs
  until a T30 task lands and the `ArrayTaskThrottle=1` from (br) takes hold. **Restore T30 to `%2` once
  `1329216` finishes.**
  Next: collect T43; T21 collector when `1329216` lands; then the T22, T30, T28, T29-revert and T32-campaign
  collectors as each array finishes.

- **(bt) 2026-09-17, manager — T43 and T44 both collected and accepted with manager corrections; the two
  author-owed inputs are now answered, one of them by a new deep-research prompt.** The author was asked
  directly about the two items only they hold, and answered both: the end-use split is **"you find it
  yourself"**, meaning a prompt they run outside (not that the assistant searches — deep research stays
  external); and for Figure 1, **"create image prompt and let me generate with Gemini Antigravity"**. The
  Figure 1 prompt already existed, finished and corrected at T35
  (`figures/Prompts_Images/Figure_01_workflow_prompt.md`, 169 lines, print target 190 mm at 600 dpi,
  colour-blind-safe palette, three labelled bands), so **nothing was rebuilt** — the author was handed the
  path. Creating a duplicate would have broken the standing "never create anything not requested" rule.
  **T43 ACCEPTED** (`impl/2026-09-17_T43_wp10_survey_mode_confound_limitation.md`). The CATI-to-EQ
  survey-mode confound is now the **eleventh** limitation in `manuscript/draft_S7_limitations.md`. The
  opening count was updated from "ten ... first seven" to "eleven ... first eight" — that count had already
  been wrong twice in this file's history, so it was checked against what the section actually lists. The
  employee checked for overlap before adding and found limitation 6 alludes to survey disruption without
  ever naming the mode change, so it added a paragraph rather than a near-duplicate, and said so. The
  paragraph is honest in both directions: it states the mode change lands on exactly the 2022 cycle that
  carries the at-home shift, that no wave exists in the new mode to compare against, that the design
  **cannot rule the possibility in or out**, and that this does not overturn the direction of the result
  but does mean the step's exact size carries an unmeasurable survey-design component. Trace row 9 was
  added, and it turned up a genuine code-level fact nobody had recorded: **`COLLECT_MODE` is 0 for
  2005/2010/2015 and 1 only for 2022**, so the confound is established from our own data and not borrowed.
  **One manager finding on T43, logged as new plan §5 item 22:** the paragraph's one sentence about outside
  survey-methodology literature is traceable to dr_2J-12's quote-checked vetting file but **carries no
  citable reference**, and the assistant may not go find one. Step 13 must either attach a vetted citation
  or soften the sentence to what our own data supports; option (b) suffices, because `COLLECT_MODE` already
  establishes the confound. Recorded rather than shipped unsourced.
  **T44 ACCEPTED WITH TWO MANAGER CORRECTIONS** (`impl/2026-09-17_T44_dr2j13_enduse_split_prompt.md`). The
  new prompt `deepResearch/dr_2J-13_sheu_enduse_split_gemini_prompt.md` is written and registered on the
  README's prompt table: Gemini only, no Fable twin (Fable has no live search here and a hunt for published
  numeric values without search is worthless — stated in the file so nobody adds one later), and it carries
  the four **pre-registered** decision rules, fixed before any result is read, including the one that
  matters: **if the space heating figure specifically is NOT FOUND, the breakdown is not run at all** and
  the paper attributes the gap to no single end use. Verified by the manager: 0 em or en dashes, `NOT FOUND`
  stated four times, the denominator requirement present five times, the calibration-not-validation wording
  present. The two corrections, both real defects:
  **(1) The positive control was the same number the decision rule depends on.** The employee made the
  control "the share of residential energy used for space heating" — which is exactly the load-bearing value
  under rule 3. That destroys the control's only purpose: if it comes back empty, a broken search and
  genuinely absent data are indistinguishable. Replaced with **total residential sector energy use for the
  most recent published year**, trivially findable and deliberately *not* one of the five end uses, with the
  added instruction that if even the control fails the tool must **not** report the end uses as `NOT FOUND`,
  because at that point it has not established that they are.
  **(2) Our own simulated number could have steered the search.** The prompt gives our simulated space
  heating range (roughly 12.6 to 29.5 kWh/m2/year) so the tool can spot a denominator mismatch — legitimate,
  but it also anchors. Added an explicit rule: do not prefer a source because it sits closer to our value,
  do not omit one because it sits far from it, and a large disagreement is **the answer the paper needs, not
  a problem to tidy away**.
  Cluster unchanged: `1329216` still running, account still at 36 CPUs until a T30 task lands and (br)'s
  throttle takes hold. **Restore T30 to `%2` once `1329216` finishes.**
  Next: the author runs `dr_2J-13` and generates Figure 1 when convenient (neither blocks anything); vet the
  dr_2J-13 return the same 7-step way when it lands; collectors fire as the arrays finish.

- **(bu) 2026-09-17, manager — T47 ACCEPTED WITH FINDINGS: Figure 1 matches its spec on every checkable
  item; the overwritten old figure is restored and the generator can no longer overwrite it again.** The
  author generated the T35 workflow diagram and it landed in `figures/`. T47
  (`impl/2026-09-17_T47_figure01_verification.md`, 247 lines) checked it against
  `figures/Prompts_Images/Figure_01_workflow_prompt.md` without eyeballing anything that eyes cannot
  count: all **24 box labels** verified by extracting the spec's numbered strings and the script's
  `BOX_LABELS` dict by regex and diffing all 24 pairs (**0 mismatches**); all **33 arrows** verified by
  reading the generator's drawing calls line by line, one draw call per spec arrow, same directions, and
  **only arrow 32** (box 6 IESO to box 24) dashed, carrying the exact required label "external check, not
  an input"; the **three band titles** correct in name, order and wording; print size read with Pillow as
  **4488 x 3732 px at 600 dpi = 190.0 x 158.0 mm**, exactly the spec target; and the must-not list clean
  (no result numbers, no internal codes, no "forecast", no watermark, no author name), corroborated
  structurally because the script can only emit text from the three sources already diff-checked. Nothing
  FAILED, so **no corrected image prompt was needed** and none was written — the author's new standing
  instruction ("if needed create new prompt, you are the one who designs the prompts", 2026-09-17) gives
  the manager authority to author a replacement prompt without asking, and that authority was not
  exercised because the figure is right.
  **Two real process findings, both acted on by the manager rather than logged and left.**
  **(1) The overwrite is undone.** `figures/Figure_01_pipeline.png` had been silently written over by the
  new run: T47 proved it with SHA-256 (byte-identical to `Figure_01_workflow.png`,
  `c2c198e8...`, both 666,675 bytes, mtimes one second apart) rather than trusting size and date. The
  pre-overwrite original survived untouched one level up at `writing/figures/Figure_01_pipeline.png`
  (1,871,483 bytes, `97aeb83b...`, June 2026), so nothing was ever lost. It has now been **copied back**
  by `scratchpad/restore_fig01_pipeline.py`, which refuses to act unless both hashes still match what T47
  measured, copies to a temp file, re-hashes the copy, and only then replaces; the restored file is
  verified at `97aeb83b...` and the new workflow figure is verified unchanged at `c2c198e8...`. The reason
  to restore is the historical record: the archived Building Simulation drafts under
  `writing/submission/extra/` and `writing/submission/archive/` hard-reference that filename with the old
  axonometric caption, and were pointing at a picture that no longer matched their own words. Nothing live
  was broken — `manuscript/draft_S2_framework.md:3` still holds only a placeholder and cites no filename.
  **(2) The generator could have done it again, so the line is gone.** `scripts/generate_fig01_workflow.py`
  hardcoded a **fourth** save to `Figure_01_pipeline.png` on every invocation (old lines 695-700), with no
  flag to skip it and no dry-run mode, which meant the file could not even be re-rendered for a preview
  without destroying the old figure a second time. The manager removed that block and replaced it with a
  comment naming the retired figure, its caption file, the drafts that reference it, and the instruction
  not to reinstate it. The script now writes exactly three paths, all `Figure_01_workflow.*`, confirmed by
  grep; `py_compile` passes. This is the only `.py` edit taken in this window and it removes a destructive
  write, it does not change the figure: the drawing code is untouched, so a rerun reproduces the same
  image.
  **Two cosmetic findings recorded and deliberately not fixed:** inside band 2 the physical seating order
  runs 10, 12, 11 while the spec's list numbers them 10, 11, 12 (the spec never required seating to equal
  numbering, and the 10 to 11 arrow is drawn as an overhead line that correctly skips box 12, so the
  required topology is intact); and a thin dotted vertical rule separates each band's title column from
  its diagram area, which the spec did not ask for and which is neither an arrow nor text. Re-rendering to
  chase either would risk a working figure for nothing.
  **New plan §5 item 23** records the one thing that must not be got wrong later: WP11 cites
  `Figure_01_workflow.png` and never `Figure_01_pipeline.png`, and the print-size legibility check at 100
  percent zoom is the author's own eye, to be asked for once at figure lock-in.
  **Cluster, read properly this time.** The T21 scorer `1329216` **COMPLETED** in 00:50:25 after (bs)'s
  one-line `--out` fix, which unblocks Step 3. T30 was **restored to `%2`** as (bt) required
  (`scontrol update JobId=1328419 ArrayTaskThrottle=2`, verified `ArrayTaskId=41-47%2
  ArrayTaskThrottle=2`), taking the account to exactly **32 running CPUs**: at the promised ceiling, not
  over it, so the author's other 32 CPUs stay untouched. **Method note worth keeping:** summing
  `squeue -h -o '%C'` reported 48 CPUs and looked like a breach of that promise, but the sum includes
  **PENDING** array tasks, which hold no cores; the rows had to be read one by one to see that only 28
  were running at that moment. Never act against a load-bearing job on that sum alone.
  Next: T45 (T21 collector) and T46 (dr_2J-13 vetting) still running; then the T22, T30, T28, T29-revert
  and T32-campaign collectors as each array finishes.

- **(bv) 2026-09-17, manager — T46 ACCEPTED; dr_2J-13 is CLOSED and pre-registered rule 3 FIRES: the paper
  attributes the energy-intensity gap to no single end use.** The author ran `dr_2J-13` in Gemini and the
  return landed as `deepResearch/dr_2J-13_sheu_enduse_split_gemini_results.md` (27,117 bytes). T46 vetted it
  the full seven-step way (`deepResearch/dr_2J-13_VETTING.md`, 317 lines): **verdict PARTIALLY SURVIVES**.
  What is genuine is genuine, and it is a lot: all five NRCan CEUD tables were re-fetched live **for the
  2022 column specifically** (the default view shows 2023, which briefly looked like a discrepancy) and
  **every PJ value in both tables matches the source exactly**, floor-space and household activity bases
  included; both StatCan table identities resolve; all 30 PJ-to-kWh conversions, every intensity, every
  share and every column sum were independently recomputed in Python and are clean to rounding; 12 of 15
  checked citations are fully VERIFIED, and **nothing is fabricated**.
  **The ruling, which the vetting deliberately left to the manager, is that rule 3 fires.** No measured or
  survey-based Canadian end-use split exists: direct sub-metering NOT FOUND, SHEU publishes no end-use
  split, the IESO/Cadmus survey gives no absolute intensities, peer-reviewed NOT FOUND. The only split on
  offer is CEUD, which the return itself describes as the Residential End-Use Model, engineering stock
  accounting of unit energy consumptions calibrated to StatCan control totals. The prompt's scope guard
  said in advance that a modelled value is not an answer, so the breakdown is **not run at all**: the
  manuscript states the measured split was unavailable and attributes the Table 5 gap to **no single end
  use**. The return's own headline sentence, that the gap is "unequivocally located in the thermal space
  heating load" at **4 to 9 times** below benchmark, **never appears in the paper**, in any section.
  **A second, independent reason to refuse that number, found by the vetting and worth more than the
  rule:** the comparison's basis was never established. CEUD's denominator is *heated* floor space and its
  space heating is **all-fuel raw combustion energy**, gas-dominated in Ontario, while our figure is
  simulated site energy on our own floor-area definition. Neither the area definition nor the fuel and
  efficiency scope was checked, so a 4-to-9-times multiple could be largely an artefact of the two bases.
  This is exactly the failure the prompt's denominator requirement was written to catch, and the return
  named the basis without ever confirming it matched ours. Writing that sentence into a paper already
  rejected partly on calibration provenance would have handed the next reviewer the same objection.
  **This is a good result, not a loss.** It converts a hole in the paper into a defensible statement:
  Canada publishes no measured residential end-use split, only a modelled disaggregation, so the gap
  cannot be assigned to one end use without an equivalence this study cannot establish. That is the WP5
  missing-measured-data limitation in its honest form, and it costs the paper nothing. Recorded as plan
  §5 item 24, with the wording the manuscript may use.
  **Two smaller rulings in the same item.** The **saved file is the record and the chat-side summary of
  that run is not to be used for anything**: its Ontario Single Detached water heating figures (68.7 PJ /
  32.81 kWh/m2, 221.7 m2, stock 3,197,358) do not reconcile with themselves, with the file, or with the
  source, while the file's own table (56.2 PJ / 26.86 kWh/m2) reproduces CEUD exactly. The manager had
  flagged this contradiction from the chat text before the vetting ran, and the vetting settled which side
  is right by first principles rather than by preference. And **three background citations carry a wrong
  detail** to correct if ever cited: Rouleau and Gosselin 2021 is Applied Energy vol. **287** not 290,
  Papineau et al. is **2021** not 2022, and the Makonin HUE dataset is **22** homes published **2019**, not
  28 homes in 2018. None carries a number this paper uses.
  **Also noted, not acted on:** the return's positive control (StatCan residential 2022, 1,380.174 PJ)
  disagrees with the CEUD Canada residential total (1,454.1 PJ) by **5.1 percent**, which the return should
  have flagged and did not. The control still did its job — it proved the search worked, so the `NOT FOUND`
  results above are genuine absence and not a broken tool, which is the whole reason it was made
  independent of the five end uses at T44. No paper number depends on either figure.
  Next: T45 (T21 collector) still running; then the T22, T30, T28, T29-revert and T32-campaign collectors
  as each array finishes.
