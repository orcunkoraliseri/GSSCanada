# 5J Methods Design: reading retrofit and cooling state from permits, with abstention, into an occupied stock

Written 2026-09-22 by the manager, on the author's request "start the 5J methods design". This is the
working doc for 5J from now on; the kickoff note stays as the subject record. State lives here: the
Progress Log at the end is the resume point. Edit in place.

Status: **DRAFT v1. One decision open (D-5J-3, section 9). Thresholds in section 7 are DRAFT until
frozen by checksum at the end of WP1.**

---

## 1. The paper in one paragraph

Canadian cities do not know which homes have new windows, added insulation, a heat pump or air
conditioning. Permits record some of this work, in short clerk text, in French in Montreal and
English in Toronto; much of it (all heat pumps and air conditioners in Montreal) needs no permit at
all, so a missing permit means "unknown", never "none". We read that text with an open-weight
language model that gives a set of answers or abstains, with conformal coverage stated per group; we
combine what it reads with area shares (EnerGuide by postal area, StatCan by city) into a probability
for each building's state; and we carry that uncertainty through paired EnergyPlus runs driven by GSS
time-use occupancy, to show how much the unknown state changes heating and cooling demand and the
indoor heat felt by the people actually at home.

## 2. Research questions

* **RQ1 (reading).** On short French and English permit text, how well does an open-weight language
  model recover five retrofit events, against human labels, compared with a keyword rule, a
  Gunay-style association-rule baseline and a small fine-tuned encoder?
* **RQ2 (knowing when not to answer).** With split conformal prediction, what coverage and what
  abstention rate does the reader reach, per building group and per decade, and does the coverage
  survive a change of city and language (Montreal to Toronto) or of period (before and after 2010)?
* **RQ3 (building state).** When read events are combined with area shares and a detection rate for
  unpermitted work, how far is each building's state known, and do the resulting shares fall inside
  the EnerGuide and StatCan area figures?
* **RQ4 (what it changes).** How much of the spread in stock heating and cooling demand, peak demand,
  and occupied-hour indoor overheating comes from the unknown retrofit and cooling state, compared
  with the spread that comes from who is at home (GSS occupancy)?

RQ4 keeps the series spine (paired EnergyPlus, occupancy effect isolated). It stays distinct from the
NSERC subject: no power failure, no survivability window; supply is always on.

## 3. Scope, decided

| Item | Decision | Why |
|---|---|---|
| Development city | **Montreal**: permits (CC BY 4.0, 560,309 rows, coordinates on 96.8 %) | French text, open licence, coordinates, open assessment roll for vintage and dwelling count |
| Held-out city | **Toronto**, reading only (RQ1, RQ2) | English text, tests shift; no open roll with vintage, so no Toronto stock run |
| Stock and simulation | **Montreal only** | Linkage and vintage exist only there |
| Target labels | Windows replaced (W), insulation added (I), heat pump installed (HP), central air conditioning installed (AC), heating system or fuel change (F) | Five events the text can name; plus two reset events, new construction (N) and demolition (D) |
| Reference year | State at end of 2022 | Matches GSS 2022 cycle and StatCan 2021 and 2023 tables |
| Weather | Montreal CWEC 2020 typical year, plus the actual 2018 year (July heat wave) | Present climate only; future weather stays out (it belongs to the NSERC line) |
| Outside benchmark | New York City (permits plus Local Law 84), named in the paper as the route for per-building truth; **not run in v1** | Keeps the build finite; revisit only if RQ3 gates cannot be scored |

## 4. Data, and what each source is for

Roles as in brief section 10: L1 input text, L2 label, L3 area check, L4 link.

| Source | Role | State |
|---|---|---|
| Montreal permits (`nature_travaux`) | L1, L4 | Checked 2026-09-22; to be re-downloaded and frozen with checksum in WP0 |
| Toronto permits, 3 files | L1 | Checked; dedupe by permit number; strip the "HVAC -" prefix; dataset licence field blank, portal OGL-Toronto to be confirmed in WP0 |
| Montreal assessment roll (unités d'évaluation foncière) | L4, vintage, dwellings, building type | Named as open (CC BY) by T41 at source; columns not yet opened by us: WP0 |
| EnerGuide open package | L3 by postal area (FSA): heat pump, AC, furnace, insulation | Named at source by T40; never opened by us: WP0 counts Montreal (H) and Toronto (M) FSAs and rows per FSA |
| StatCan 38-10-0019-01 (AC), 38-10-0286-01 (primary heating) | L3 by city, 2013 to 2023 | Named at source by T40; WP0 pulls Montreal and Toronto rows |
| Human labels on permit text | L2 | Do not exist; WP1 makes them (decision D-5J-3) |
| GSS time-use 2022, Census PUMF 2021 | Occupancy | In hand, through the 2J pipeline |
| 2J Montreal EnergyPlus models (detached, attached, mid-rise, high-rise; NBC 9.36 / NECB 2017; v24.2) | Simulation base | In hand: `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/` |

Known bias, written in now: EnerGuide homes chose to be audited, so their shares lean towards
upgraded homes [INFERENCE]; they are an area check, never a per-building label.

## 5. Method, in seven work packages

### WP0. Freeze and inventory (sonnet agents, no design choices)
Download and checksum every source in section 4; write row counts, column lists and fill rates
actually read. Toronto licence: quote the portal page. EnerGuide: rows per Montreal FSA, and which
columns name heat pump, AC and insulation. Assessment roll: vintage and dwelling-count fields and
their fill rate; share of permits that join to a roll unit by coordinates within 15 m (then by
address). Inventory the 2J Montreal models: what heating system and envelope each carries, which
fields a retrofit would change. Output: `impl/2026-09-22_wp0A_permits_roll.md` and
`impl/2026-09-22_wp0B_areatruth_models.md` (task doc `impl/2026-09-22_wp0_task.md`).

### WP1. Labels and sampling
* **Label spec** (`5thJ_02_Label_Spec.md`): for each of the seven labels, the rule, French and English
  positive and negative examples, and the traps already known ("isolation" for sound or fire
  separation is not I; "même ouverture" window work is W; Toronto boilerplate is not F).
* **Unit of labelling**: one permit text. Each label takes yes, no, or "cannot tell from this text".
* **Sampling frame**: residential permits only. Strata: keyword hit group × decade × building type,
  with rare groups (HP, AC, I) oversampled. Every metric is reported per stratum and re-weighted to
  the population by known inclusion probabilities.
* **Sizes**: Montreal 2,000 (dev 400, calibration 800, test 800); Toronto 600 (calibration 300, test
  300). About 2,600 short texts, roughly 10 to 12 hours of reading.
* **Agreement**: 400 texts labelled twice, blind; Cohen's kappa per label reported. A label under
  kappa 0.6 is merged or dropped before any model is scored.
* **Test sets are sealed**: written once, checksummed, and not opened until section 7 is frozen.

### WP2. Readers (RQ1)
Four readers, all scored on the same sealed test rows:
1. Keyword rule (French and English stems, with the negation and trap list from the label spec).
2. Gunay-style association rules, re-implemented from the paper's description.
3. A small fine-tuned encoder (multilingual or French-first), trained on dev plus a training split
   carved from calibration only if WP1 sizes allow; otherwise few-shot only.
4. An open-weight instruction model on one A100 80 GB, constrained JSON output, per-label answer
   probabilities taken from the answer-token log-probabilities. Two or three model families are tried
   on the dev split only; the winner is pinned (name, revision hash) before the test set is opened.

The language model counts as better only if it beats the best of readers 1 to 3 (section 7). A tie
is reported as a tie: window work is already keyword-findable.

### WP3. Abstention with stated coverage (RQ2)
* Split conformal per label, nonconformity = 1 minus the probability of the true answer; α = 0.10.
  The output per label is {yes}, {no}, or {yes, no}; {yes, no} is an abstention.
* Mondrian (group-conditional) versions by building type, by decade, and by borough group, so that
  coverage is stated per group, not only on average.
* Shift tests: calibrate on Montreal, test on Toronto unchanged (expected to break, and reported as
  such), then recalibrate on the 300 Toronto calibration rows; calibrate on permits before 2010, test
  on 2010 and later.
* Also reported: set size, abstention rate, and the accuracy-coverage curve for plain selective
  prediction, so a reader can compare against simple thresholding.

### WP4. From permit events to building state (RQ3)
* Join permits to roll units (WP0 rule). A building's history is its ordered permits to 2022; N or D
  resets the history.
* For each building b and element e: if any permit has set {yes} for e, the state is "upgraded" with
  probability 1; each abstained permit contributes its conformal-calibrated probability; if nothing is
  read, the state falls back to the prior.
* **Prior** from area shares: π(e, FSA) from EnerGuide, scaled to the StatCan city share; vintage
  enters through the roll's construction year.
* **Unpermitted work**: a detection rate d(e, city) is the share of real installs that leave a
  readable permit. For HP and AC in Montreal d is near zero by rule (no permit needed); for W and I it
  is estimated by comparing read counts per FSA against the area shares. Then
  P(upgraded | nothing read) = π(1 − d) / (1 − π d).
* **Check**: aggregate the building probabilities per FSA and per city; the model's 90 % interval
  should contain the EnerGuide FSA share and the StatCan city share (gates in section 7).

### WP5. EnergyPlus campaign (RQ4)
* **Geometry**: the four 2J Montreal models. Duplexes and triplexes, the bulk of Montreal's stock,
  have no own model; the attached house stands in for them, and this is written as a limitation.
* **Vintage**: three envelope levels (before 1960, 1960 to 1989, 1990 and later). The U-values and
  air-tightness per level need a Canadian source (open item O-1).
* **State combinations**: W, I (each yes or no), heating system (baseboard electric, gas or oil
  furnace, cold-climate heat pump), AC (yes or no). About 24 combinations after impossible ones are
  removed.
* **Occupancy**: 50 GSS 2022 household draws per archetype through the 2J pipeline, matched to the
  Montreal household mix from Census PUMF.
* **Design**: every run is paired: same occupancy draw across all state combinations, same state
  across all occupancy draws. Roughly 4 geometries × 3 vintages × 24 states × 50 occupancy × 2
  weathers ≈ 29,000 short residential runs; on Speed within the 32-CPU cap, about one to two days.
* Stock results are built by weighting these runs with each building's WP4 probabilities; no new
  runs are needed to redraw the stock.

### WP6. Propagation and split of the spread (RQ4)
* Outputs per run: annual heating and cooling energy, winter and summer peak hour demand, and
  **occupied-hour overheating**: hours above 26 °C and 28 °C operative temperature while someone is
  at home (from the GSS schedule), for homes without AC.
* Stock outputs: draw 1,000 stock realizations from the WP4 probabilities; report the median and
  90 % interval of each output for Montreal and per borough.
* Split: a two-factor random-effects decomposition (state draws × occupancy draws, paired) gives the
  share of spread due to unknown state, to occupancy, and to their interaction.
* Counterfactual that makes the reader matter: the same stock with (a) prior only, no permits read;
  (b) keyword reader; (c) language-model reader with abstention. The narrowing of the interval from
  (a) to (c) is the value of reading the text.

## 6. What makes it new (kept to what the searches support)

Retrofit and cooling state read from French and English record text, with abstention at stated
coverage, carried as uncertainty into a stock model with time-use occupancy. Nearest work, all read
at source: Gunay et al. 2023 (keywords and rules, no equipment, no abstention), Zhang et al. 2020
(BERT, work type, no abstention, no French), Wu et al. 2026 Geo2UBEM (language model tunes model
inputs against a benchmark, reads no records), Borrotti 2024 (conformal on simulated loads, not text),
Geske and Voelker 2025 (refurbishment uncertainty through an urban model, Germany). Not "first
language model for urban energy model inputs".

## 7. Gates (DRAFT; frozen by checksum at the end of WP1, before any test row is scored)

| Gate | What | DRAFT threshold | Must be seen failing by |
|---|---|---|---|
| G5J.1 | Label agreement | kappa ≥ 0.6 per kept label | Scoring one annotator against shuffled labels |
| G5J.2 | Reader gain | Language model macro-F1 ≥ best baseline + 0.05 on the Montreal test (re-weighted), with a bootstrap interval that excludes 0 | Scoring the model against a copy of the keyword rule |
| G5J.3 | Coverage, Montreal | Empirical coverage in [0.87, 0.93] for α = 0.10, overall and in every Mondrian group with ≥ 50 test rows | Calibrating on labels shuffled within the calibration set |
| G5J.4 | Coverage, shift | Reported, not gated: Toronto coverage before and after recalibration; before and after 2010 | (report-only) |
| G5J.5 | Abstention usefulness | Abstention rate ≤ 40 % on W at the gate α; reported for every label | Setting α = 0.01 |
| G5J.6 | Area check | The model's 90 % interval contains the EnerGuide share in ≥ 80 % of Montreal FSAs with ≥ 30 EnerGuide homes, and contains the StatCan city share for AC and heat pump | Replacing the prior with a uniform 50 % |
| G5J.7 | Base stock | Simulated Montreal residential energy intensity inside a report-only band from NRCan SHEU 2019 for Quebec | (report-only) |

A gate that cannot be computed is NOT_EVALUABLE, never PASS. The perturbation table (one
perturbation breaks exactly one gate) is written with the freeze.

## 8. Open items (not decisions for the author; the manager closes them)

* **O-1** Canadian envelope values by vintage for Montreal houses and plexes (U-values, air-tightness).
  Route: one external deep research prompt, or NRCan housing archetype data if WP0 finds it open.
* **O-2** Toronto licence (WP0). CLOSED 2026-09-22: Open Data Licence - City of Toronto (portal page).
* **O-3** EnerGuide file contents and Montreal FSA counts (WP0); G5J.6 may shrink if few FSAs pass the
  30-home floor.
* **O-4** Which heating systems the 2J models carry and whether a cold-climate heat pump can be
  swapped in cleanly (WP0 inventory). MOSTLY CLOSED 2026-09-22: gas furnace + DX cooling in all
  models; baseboard and heat pump variants to be built; one test run per variant owed (WP5).
* **O-5** Pauling 2026 (SSRN) and Jiang et al. 2025 (Energy) still unread; low priority, before
  submission.
* **O-6** Venue: decided later, when RQ1 results exist.

## 9. The one decision for the author

**D-5J-3. Who writes the human labels (WP1)?** About 2,600 short permit texts, 10 to 12 hours, plus
400 read twice by a second person. The labels are the only per-text truth in the paper, so they
cannot come from a language model. **Recommend (a): the author labels, a colleague reads the 400
agreement texts blind.** (b) Two paid research assistants. (c) The author alone, agreement measured
by the author re-labelling 400 texts two weeks later (weaker).

## 10. Order of work

WP0 (agents, now) → WP1 label spec and sample (manager and agent) → labels (author, D-5J-3) →
freeze section 7 → WP2 and WP3 → WP4 → O-1 closed → WP5 → WP6 → writing.

---

## Progress Log

- 2026-09-22 (manager): design v1 written after Geo2UBEM read. Montreal is the development and stock
  city; Toronto is the held-out reading test; five labels plus two reset events; split conformal with
  Mondrian groups; building state = read events + area prior + detection rate; about 29,000 paired
  EnergyPlus runs on the four 2J Montreal models × three vintages. Open: D-5J-3 (who labels); O-1 to
  O-6. Next: WP0 freeze and inventory by a sonnet agent.
- 2026-09-22 (manager): WP0 launched as two sonnet employees in parallel (task doc
  `impl/2026-09-22_wp0_task.md`; A = permits, roll, linkage -> `impl/2026-09-22_wp0A_permits_roll.md`;
  B = EnerGuide, StatCan, 2J model inventory -> `impl/2026-09-22_wp0B_areatruth_models.md`). Data to
  `GSSCanada\_5J_data\` (outside the repo). If either impl file is missing or IN PROGRESS on resume,
  re-launch that employee fresh from the task doc.
- 2026-09-22 (manager): **WP0-A reviewed, DONE.** Re-derived by the manager from the files: roll
  514,439 rows and sha prefix 7e3f834c match; Montreal residential permits 420,572 (accent-insensitive
  rule) and 410,123 joined by address (97.5 %) match. Two corrections to the employee's vintage split,
  measured by re-running its own join (`scratchpad/chkA2.py`):
  (1) the roll uses **9999 as a placeholder year** on 19,990 rows (and 51 rows before 1800, minimum
  1600); the employee counted 9999 as "1990 and later" and reported "missing: 0". Among joined permits
  the true split is before 1960 244,946 / 1960 to 1989 97,317 / 1990 and later 60,811 / placeholder
  9999 6,936 / before 1800 113. Rule for WP4: 9999 and < 1800 = vintage unknown, fall back to the
  borough vintage mix.
  (2) 85,376 joins (20.8 %) had several roll candidates; in **16,098 (3.9 % of joined) the candidates
  fall in different vintage bands**. Rule for WP4: when candidates disagree, carry the vintage as a
  mixture over the candidates (weighted by dwelling count), not the first row. The address join is
  kept (no coordinates in the roll CSV); the GeoJSON extract is not needed now.
  Toronto: 1,083,669 unique permits, 729,339 residential, 101,611 "HVAC -" texts (median 88
  characters). **O-2 CLOSED**: both CKAN records say "License not specified", and the portal page says
  the Open Data Licence - City of Toronto (based on OGL Ontario 1.0) covers portal data, commercial use
  allowed; cite the portal page. Employee's open questions settled: Toronto duplicate keys keep the
  cleared-file row (as done); the 2,394 extra "Residential"/"House" rows are added in WP1 (small, and
  clearly residential); building category = LIBELLE_UTILISATION.
- 2026-09-22 (manager): **WP0-B partly reviewed.** StatCan extract and IDF inventory done (see its impl
  file). The employee stopped at 186k tokens while its EnerGuide download was still running and its
  first analysis read files still being written (2019 was read at 255 MB, final size 358 MB; 2007 to
  2018 missing) — **its EnerGuide counts are void**; a fresh employee redoes them after the download
  ends. **O-4 mostly closed**: all four 2J models already carry cooling (DX coil in every system), so
  "no AC" means switching the cooling coil off; the houses heat with a gas furnace coil, but Montreal
  homes mostly heat with electric baseboards, so the baseboard and heat pump variants must be built
  (standard EnergyPlus objects: electric baseboard; air-to-air heat pump unitary system). The house
  envelopes are new-build (IECC 2024 / NBC 9.36); vintage levels replace the insulation material
  values inside the existing constructions, and houses use an airflow network for air leakage, so
  air-tightness per vintage is set through the leakage areas. One test run per variant is still owed.
- 2026-09-22 (manager): EnerGuide download finished (21 files, `download_log.txt` ALL_DONE). Old
  employee B stopped and its leftover analysis process killed. Fresh employee B2 launched on the task
  doc section "Employee B2"; it appends to the B impl file. If that section is missing or B impl
  Status is not DONE on resume, launch a fresh B2.
- 2026-09-22 (manager): author leaves until tomorrow. Handover written as the "START HERE" box at the
  top of `5J_docs_occ/PROMPTS/New_ideas_Manager_Prompt.md` (B2 check, D-5J-3 in plain words, then WP1).
