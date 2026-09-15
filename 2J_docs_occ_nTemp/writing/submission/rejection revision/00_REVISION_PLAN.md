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
Phase 5  build, check installed files, cover letter, submit (WP13)
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

Items 1–2 get stronger once WP7 step 3 exists; item 8 is the one to do before resubmitting anywhere.

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
| D1 | Scenario set for 2030 | S-Persist, S-Partial, S-Revert; add S-Grow only if an external source gives a number |
| D2 | Run the simple-schedule arms (WP3)? | Yes, both arms — it is the direct answer to Reviewer 1's first point |
| D3 | Run the older-envelope sensitivity (WP7.3)? | Yes, SingleDetached only (600 runs) |
| D4 | One post-relink panel for all five years (§4 risk)? | Decide after WP1 results |
| D5 | Approve Phase 2 compute (~11–13k runs) | Yes, after wall-clock is estimated from the ledgers |
| D6 | Venue | See §8 — decide at Phase 4, not now |

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

---

## §9 What closes this round

- [ ] §7 decisions answered by the author
- [ ] WP1 done; the +8.3 pp gap re-derived before and after; all 2030 numbers recomputed
- [ ] WP2–WP9 done or explicitly declined, each with its implementation doc
- [ ] Deep-research returns vetted by the author before any new citation
- [ ] Every one of the 42 triage rows in §2 mapped to a change in the new manuscript (keep this map;
      some journals ask about prior submissions)
- [ ] Carried items closed: crosswalk, 600 dpi, prior-paper status, novelty-matrix search
- [ ] Venue chosen and recorded in `02_journal_options.md`
- [ ] Manuscript rebuilt; `submit_check.py` green on the installed files
- [ ] `00_README_submission.md`, the revision-decision prompt, and the memory file updated to the new
      archive paths and outcome in the same pass

---

## Progress Log

- **2026-09-15** — Rejection received (BUIL-D-26-01113, 3 reviewers). Submitted files moved to
  `archive/` (18 files, SHA-256 identical before/after). This plan written. Nothing computed, no
  manuscript edits. Next: author answers §7.
