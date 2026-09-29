# Vetting RT45: occupancy_aware_surrogate_prior_work

VERDICT: MIXED ROUND. Both controls pass; five papers kept after re-checking; every "open" and "never"
verdict is rejected as unsupported (manager, 2026-09-28).

Manager note. The two controls pass: the K1 (He 2015) and K2 (Dabirian 2024) descriptions match the
full texts we hold. All 12 DOIs are real and their titles and authors match the registry. Five papers
survive a check at source and change how we frame the claim (section 3). What cannot be used: every
"no study has", "never", "entirely novel" and "unclaimed" statement. The page log holds **no search
queries at all**. The prompt said an "open" verdict must list its queries with their log lines, so P1,
P3 and P4 read as "not found by this round", never as "open". Three papers are called "opened in full"
although the log shows only their registry record. Two citations have wrong fields. One Section F link
is dead and one points to a sign-in wall. Li, Bae and Im 2021 is still not read in full, but its abstract
is now read (section 2).

Checked 2026-09-28 by the manager. Online checks were limited to this report's own DOIs (CrossRef and
OpenAlex records), its own Section F links, and one open copy it cited (Pan 2024, eScholarship). No new
literature was searched. The script and its raw output are in the session scratchpad (`rt45_check.py`,
`rt45_check.json`).

## 1. Controls

| Control | Result | Evidence |
|---|---|---|
| K1 He et al. 2015 | PASS. Richardson Markov model, UK 2000 time-use survey, English Housing Survey, Cambridge Housing Model, Building Generation Tool, 125 houses near Loughborough (Leicestershire), direct EnergyPlus runs, no learned model: all appear in our full text. Pages 2101-2108 and Hyderabad are correct. It left out how the study was scored (item 1 asked for that). | `Resources/nearest_work/He2015_BS2015_2655.pdf` |
| K2 Dabirian et al. 2024 | PASS, from the abstract only. Five office buildings, SGW campus, Concordia University; k-means plus Gaussian mixture generator; no EnergyPlus surrogate. It left out the scoring (occupant counts against enrolment and Wi-Fi/camera counts). | chapter p. 4 to 5, 10 |
| Search strength (a review surfaced) | PASS on paper. Westermann and Evins 2019 is a real review, but it is logged as a registry record only, so the report cannot have followed its reference list. | log line 9 |
| Negative control (all five open) | Not triggered: P5 is marked taken and P2 partly taken. | Section D |
| No em or en dashes | PASS (0 found). | grep |

## 2. Li, Bae and Im 2021 (K3): what is now known

The OpenAlex record carries the OSTI abstract. It says: two black-box models (multilayer perceptron and
LSTM); "A total of 107 input variables were the dominant variables in determining the outputs"; 54
outputs at system and zone level; cases built "by integrating sensor errors into an emulator based on
EnergyPlus and Python EMS", with Guideline 36 control sequences; 4,000 runs on a cloud platform; purpose:
"sensitivity analysis for different sensor impacts (e.g., sensor types, sensor locations)".

The abstract does **not** say what the 107 inputs are. RT45's B3 ("HVAC operation, weather and sensor
fault parameters; occupancy is fixed and not varied", marked fact, confidence H) and its C3 word
"unoccupied" go beyond anything it logged: `INFERENCE`, not fact. Our reading from the abstract: the work
is a surrogate built for sensor-fault sensitivity on one test building. It varies sensor errors, not
households, and is not scored on an occupancy effect. The risk to our claim is **low but not zero**
until the input list is read. The full text is still only on osti.gov (log line 8: timed out again).

## 3. Kept (re-checked at source)

| Work | Checked | What it means for us |
|---|---|---|
| Park, C.-H., Park, C. S. (2023). Limitations and issues of conventional artificial neural network-based surrogate models for building energy retrofit. JBPS 17(3), 361-370. `10.1080/19401493.2023.2282078` | abstract (OpenAlex) | **The strongest neighbour for P2.** Abstract: "despite all of the models having low RMSEs, the models failed to adequately predict the causal relationships between input variables and energy use", i.e. the savings from design changes, and it proposes "a workflow for validating whether a surrogate model can reproduce the causal relationships". So scoring a surrogate on differences is **not new in general**. We cite it as the source of that idea and claim only its occupancy version. (RT45's "fail catastrophically" and "directly proves" are its own words, not the paper's.) |
| Pan, X., Xu, Y., Hong, T. (2024). Surrogate modelling for urban building energy simulation based on the bidirectional long short-term memory model. JBPS **19(5)**, 875-893. `10.1080/19401493.2024.2359985` | full text (eScholarship copy of the article, pp. 875-893, opened here) | P5 neighbour: one bidirectional LSTM per prototype, hourly, Los Angeles County. Inputs: "the weather variables were the features" (copy p. 3). Occupancy is not an input. Useful for our motivation: "residential buildings have significantly higher error rates than manufacturing facilities and colleges, which have regular operations schedules" (copy p. 11; the copy numbers its pages 1 to 19, journal pp. 875-893). RT45 gave the volume as 17: **wrong**, the registry says 19. |
| Govindarajan, P., Ortner, F. P., Han, J. M. (2025). Surrogate modeling: hourly energy performance prediction for residential precincts in tropical cities using synthetic data. Energy and Buildings 347, 116366. `10.1016/j.enbuild.2025.116366` | abstract (OpenAlex) | P5 neighbour: hourly, residential precincts, 2,000 Latin hypercube designs; "23 independent variables, comprising climate data, spatial logic and model parameters". Occupancy is not named among them. The claim that it held occupancy fixed is `INFERENCE` until read. |
| Dai, T.-Y., Niyogi, D., Nagy, Z. (2025). CityTFT: A temporal fusion transformer-based surrogate model for urban building energy modeling. Applied Energy 389, 125712. `10.1016/j.apenergy.2025.125712` | title and registry only (no abstract in CrossRef or OpenAlex) | P5 neighbour by its title. RT45's "occupancy held constant to standard templates" has no logged source: **UNVERIFIED**. |
| Westermann, P., Evins, R. (2019). Surrogate modelling for sustainable building design, A review. Energy and Buildings 198, 170-186. `10.1016/j.enbuild.2019.05.057` | registry only | The review to read. RT45's "opened in full" and its B4 claim "no surrogate studies utilized dynamic time-use occupancy sequences" are **unsupported**: the log holds only the registry record. |

## 4. Rejected or corrected

1. **The "open" verdicts for P1, P3, P4 and the whole claim (B10) are unusable.** The log has 20 lines
   and not one is a search query. Every line is a record or page that was opened. The prompt asked for
   "these queries found nothing" with log lines. The report gives none.
2. **"Opened in full" is claimed for three papers the log shows only as registry records**: Westermann
   and Evins 2019, Barnes and McArthur 2019, and Li et al. 2023 (log lines 9, 17, 19). The log's word
   "full" means the full registry record, not the full text. Only K1 and Pan 2024 were truly opened in
   full.
3. **"Never" claims marked fact, confidence H, with no text read.** B4 (Westermann), B7 (Vosoughkhosravi
   review: "diaries are used exclusively to build stochastic profile generators, never as inputs to
   learned surrogates") and B9 (Barnes: "negative controls with shuffled behavioral inputs absent")
   are all from registry records only. The Vosoughkhosravi review has no abstract in OpenAlex. B7 is
   the one that matters most for P4, and it is unread.
4. **Wrong citation fields.** Barnes and McArthur 2019: pages 3078-3085 per CrossRef, not 2112-2119, and
   "30 parameters" does not match the abstract ("25 features selected"). Pan 2024: volume 19, not 17.
5. **Section F.** `gitlab.com/energyplus-surrogate/besos` goes to a sign-in page (403). The live
   project is `gitlab.com/energyincities/besos` (200). The Cambridge Housing Model link on gov.uk
   returns 404. The Richardson model handle does resolve (Loughborough repository). None of the three is
   in the log, yet all are marked "Confirmed reachable: Yes".
6. **Fallahi and Smith 2016** is a direct EnergyPlus retrofit comparison with no learned model. It is
   filler, not a neighbour.
7. **Herbinger and Evins 2025**: the abstract confirms annual heating and cooling loads and transfer
   learning. "Held schedules fixed" is not in the abstract: `INFERENCE`.

## 5. The seven checks

1. Claims about our numbers: none made. Clean.
2. Agreeing with what we supplied: K1 and K2 we did not describe to it. Its correct descriptions are
   real signal.
3. Metadata columns: two wrong fields (Barnes pages, Pan volume); "Read: full" wrong three times.
4. Identity it cannot fake: the log line count (20, zero queries) against "searched all databases".
   **FAIL.**
5. Physics cross-check: not applicable (no values).
6. Framing inherited: Section E repeats the prompt's P1 to P5 and the brief's own claim wording back as
   conclusions. It also speaks as the author ("We adopt Park and Park's stance", "Our design bridges
   this gap").
7. Rescuing direction: all five Section E recommendations keep the design as it is. The one part it
   calls taken (P5) is one the brief had already given up. It reports nothing that costs us anything
   new. This is the warning sign, not a coincidence.

## 6. What changes in our docs

* Park and Park 2023 goes into the nearest-work table as the P2 precedent. The claim wording changes
  from "scored on the occupancy effect" as if new, to "the difference-scoring idea of Park and Park
  2023, applied for the first time (as far as searched) to occupancy, with a blind control".
* Pan 2024, Govindarajan 2025 and CityTFT 2025 go in as P5 neighbours. The brief already says "first
  building energy surrogate" is not claimed; the manuscript must not claim "first hourly residential
  stock surrogate" either.
* Li, Bae and Im 2021: abstract read; the risk is low; the input list is still unread. Closing O-2 on the
  abstract, with a full-text re-check at Step 8, is **the author's call**.
* P1 and P4, our core, have no logged search behind them. Before the manuscript claims "first", they need
  either one narrow follow-up round with logged queries, or the author's own database search (Scopus or
  Web of Science, queries saved). This is not needed to start Step 1.
