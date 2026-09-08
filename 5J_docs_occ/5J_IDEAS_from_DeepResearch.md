# 5J ideas drawn from the T-series deep research

Written 2026-09-07 from the seventeen returned reports `RT01` to `RT11` and `RT13` to `RT18` in
`5J_docs_occ/DeepResearch/`. This is an ideas document, not a decision. The author chooses the angle
after `T12` adjudicates the contradictions listed in section 6 and after the mechanical vetting notes
(`VETTING_RT<NN>.md`) are read.

**Vetting status.** Sections 1 to 5 were drafted before the mechanical checks returned; every number in
them is *as reported by Gemini*. The checks then landed the same evening, and the verdicts are at the top
of each `VETTING_RT<NN>.md`. Summary, 2026-09-07:

| Verdict | Reports | What it means for this document |
|---|---|---|
| ACCEPTED | `RT05`, `RT07` | rows may be quoted with their vetting note |
| ACCEPTED WITH STRIKES | `RT01`, `RT03`, `RT06`, `RT10`, `RT11`, `RT13`, `RT14`, `RT15`, `RT16`, `RT18` | quote only rows not struck in the note |
| FAILED ROUND | `RT02`, `RT04`, `RT08`, `RT09`, `RT17` | routes only; no row, count or ranking may be quoted |

Three consequences for the ideas below. First, `RT02`, the ranking report, failed on identities
(fourteen of twenty-three DOIs resolve to unrelated papers), so the `A9 > A2 > A7` order in section
1.3 is now a hypothesis with no verified landscape behind it. Second, `RT17` failed, so idea 3 (`A7`)
has no verified prior-art row at all; its openness rests on absence only. Third, the Concordia
winter-outage paper cited in idea 1 (`RT15` C4) has a DOI that resolves to an unrelated paper, so that
competition caution is unverified either way. The ten OpenAlex counts in `RT01` reproduced exactly; the
`RT06` "579 papers" count did not. Section 6 lists the defects found by reading; the vetting notes add
the identity failures row by row.

The angle codes `A1` to `A10` are those of `00_MASTER_BRIEF.md` section 4. `A11`, `A12`, `A13` are
new formulations proposed by `RT02` and are defined in section 3 below.

---

## 1. What the reports agree on

### 1.1 Gaps confirmed as open by more than one report

| Gap | Reports that reached `NOT FOUND` or "zero studies" | Angle it opens |
|---|---|---|
| Stock-scale overheating with heat-responsive or demographically resolved presence | `RT04` B4, `RT05` B1 and G, `RT08` B3 and G | `A2` |
| Dynamic or demographically resolved occupancy in passive-survivability studies | `RT15` B1 and B2, `RT01` C6 quote, `RT11` matrix 1 | `A9` |
| Time at home in any official energy-poverty indicator | `RT08` B4 and G | `A6` (as a lens) |
| Conformal or distribution-free bounds on a physics-based UBEM | `RT17` B2 and G, `RT02` B4 | `A7` |
| Abstention or calibrated uncertainty in LLM extraction from building records | `RT17` B1 | `A7` |
| Demographic time-use inside a multi-driver 2050 stock projection | `RT14` B2 and G | `A4` |
| Hindcast of any bottom-up UBEM projection against realised data | `RT14` G | `A4` (as a requirement) |
| Cross-platform or run-to-run reproducibility reported for a UBEM | `RT06` B3 and G | engine positioning |
| Dwelling-level division without a core zone, with provenance, in an open tool | `RT06` B1, B2, D | `A11`, engine positioning |
| Pretrained activity-diary model with measured cross-country transfer | `RT07` B1 and G | `A3` (as a warning) |
| Privacy guidance for synthetic occupancy in building-energy journals | `RT18` B6 and E | `A12` |

### 1.2 Doors the reports call closed or crowded

| Closed or crowded | Reports | Consequence |
|---|---|---|
| Single-building LLM to IDF translation and LLM agents over BEM | `RT01` G1, `RT02` A1 rank 11, `RT03` A and E | `A1` dropped; "agent adds nothing" objection unanswered |
| Occupant-centric demand flexibility from archetypes | `RT01` C7 saturated, `RT02` A5 rank 12 | `A5` dropped |
| Mixed-use reference band as a standalone paper | `RT02` A10 rank 13, `RT16` A and E | `A10` becomes a 3J appendix or a short communication |
| Single-country time-use schedule generation | `RT04` E2 | never the contribution again |
| Static-archetype overheating under future weather | `RT05` G3 | `A2` must carry the presence module or it is taken |
| Census plus satellite land-surface-temperature vulnerability maps | `RT08` G3 | `A2` and `A6` must add building physics and presence |
| UBEM pipeline "tool papers" | `RT06` E | the engine is never the paper by itself |
| Beating a raked donor pool with a bigger autoregressive LLM | `RT13` A, D row 1, `RT02` A3 | `A3` is the 4J write-up, not 5J |
| The label "foundation model" for a diary generator | `RT07` E2 | never use it |

### 1.3 How the ranking reports line up

`RT02` (gap check), `RT09` (funders), `RT10` (feasibility) and `RT11` (venues) all put `A9` first,
`A2` second and `A7` third. Two cautions before reading that as a result:

* `T10` and `T11` were run with `RT02`'s top three as their input, and `RT02` cites the wave-1 reports
  (`RT03`, `RT05`, `RT13`, `RT15`, `RT17`) in its own Section B. The convergence is partly inherited,
  not four independent votes.
* `RT02` passed the warmth control on `A1` and `A3` (both described warmly in the brief, both ranked
  low), but the `A9` verdicts across four reports use maximal language ("98 of 100", "can ship 100
  percent", "fits the most programmes"). README vetting rule 7 says that direction is a signal. Treat
  the `A9` ranking as the hypothesis `T12` must test, not as the answer.

---

## 2. Angle ledger

Verdicts and rows are as reported. "Lacks" is the asset the reports say we do not hold.

| Angle | Verdict across reports | Strongest supporting rows | Strongest objection (as quoted) | Lacks | Programme fit (`RT09` D, but see section 6 on its labels) | Note |
|---|---|---|---|---|---|---|
| `A1` agentic UBEM | Drop (`RT02` rank 11, score 40; `RT03` class d count zero) | `RT03` A: open at district scale | "What can an LLM do that a YAML plus a Python script cannot do faster and deterministically" (`RT03` D) | agent framework experience, error-recovery wrappers | weak except AI panels | Only defensible form: agent as EnergyPlus error diagnostician with scripted ablation (`RT03` E) |
| `A2` occupancy under heat | Open, rank 2 (`RT02` 94) | `RT05` B1, `RT08` B3, `RT04` B4 | "Without paired in-situ sensors in dozens of dwellings your indoor overheating cannot be validated at the address" (`RT02` G) | indoor temperature ground truth, heat-evacuation curves | strong Berkeley, MSCA, NSERC per `RT09` | Reframe outputs as comparative exposure hazard index, never clinical harm (`RT05` E, `RT08` E) |
| `A3` closing the transfer gap | Partly open, rank 7; keep as 4J framing | `RT13` A and E2, `RT07` A | "Scaling further is an unscientific attempt to rescue a flawed hypothesis" (`RT02` D) | Eurostat SUF access (closed to Canada, `RT07` B4) | weak | `RT13` D row 3 recommends hybrid donor-plus-edit for 5J; that is a generator redesign, not a gate change, and its evidence is thin (author-reported rows, `RT13` G3) |
| `A4` scenario axis | Open, rank 5 (`RT02` 83) | `RT14` B1, B2, E3 | "Compound uncertainty so wide the policy conclusions are untestable" (`RT02` D) | stock turnover registry, grid topology | partial | Reviewers will demand a 2000 to 2025 hindcast and official projections (`RT14` E2); adds a full factorial run matrix (`RT14` E1) |
| `A5` flexibility | Drop (`RT02` rank 12) | none | "Speculative without smart-meter verification" | grid model, tariffs | weak | |
| `A6` energy burden and equity | Partly open, rank 8 | `RT08` B4 | "Ecological fallacy; penalises disabled or elderly households" (`RT02` D, `RT08` E) | address-level income and bills (CRDCN only, `RT10` E2) | partial | Use as an equity lens inside `A2` or `A9`, with the three pitfalls of `RT08` E stated; not a paper alone |
| `A7` records with abstention, conformal UBEM | Open, rank 3 (`RT02` 93) | `RT17` B1, B2, E3 | "If the LLM abstains on 40 percent of records the prediction sets explode" (`RT02` D) | permit-to-meter ground truth; EU EPC registers are structured, so the LLM is redundant there (`RT17` G) | strong KTH and Schmidt, weak NSERC and Berkeley | Breaks the series signature (`RT11` G1); data ready in Montreal and Toronto permits (`RT10` F, `RT17` F) |
| `A8` Canadian transfer | Partly open, rank 6 | `RT02` C22 to C24 | "Tool applied to a new city is the definition of incremental" (`RT02` D) | NECB archetype library (BTAP exists, `RT10` F), utility bills | strong NSERC only | Fold into `A9` or `A2` as the Canadian arm, never alone (`RT02` E2) |
| `A9` survivability with occupants | Open, rank 1 (`RT02` 98) | `RT15` B1, B2, G; `RT11` matrix 1; `RT10` A | "Dictated by unmeasured air leakage and window habits" (`RT02` D, `RT15` D); rural stock unanswerable (`RT11` E1 obj. 6) | outage indoor sensor validation (Pecan Street exists for Texas, `RT15` F2) | strong Berkeley, NSERC, MSCA; weak Schmidt | See section 3, idea 1, for the local-competition caution |
| `A10` mixed-use bands | Drop as paper (`RT16` A) | `RT16` C1, C2 | "Engineering benchmarking, not science" | multi-city measured cohort | none | 3J appendix or *Energy and Buildings* short communication (`RT16` E2) |
| `A11` zoning bias benchmark (new) | Open, rank 4 (`RT02` 93) | `RT06` E thesis 1, `RT06` B8, B9 | "Room-scale zoning effects are known; does stock aggregation erase them" (`RT02` D) | paired multi-room sensors | partial | Zero external data; see section 5 on the overlap with 4J Step 10 |
| `A12` privacy-utility and release protocol (new) | Open, rank 9 (`RT02` 64) | `RT18` A, B8, E2 | "Withholding weights after a failed audit is ethics, not a finding" (`RT18` D) | custodian sign-off | Schmidt only | Short paper for *Journal of Privacy and Confidentiality* or *Scientific Data*, derived from 4J's audit |
| `A13` counterfactual shock synthesis (new) | Open, rank 10 (`RT02` 64) | `RT13` E2 | "Extrapolation beyond training bounds is hallucination, not projection" (`RT02` D) | any ground truth for the shock | partial | Hold; the only use of the generator that `RT13` leaves it |

---

## 3. Ideas worth carrying into T12

Each idea names the reports that support it, the assets it uses, what the engine lacks today (from the
`_scan/` digests), the blocker, and the risk the reports did not raise.

### Idea 1. Who is home when the power fails (`A9`, with `A8` as the Canadian arm)

**The claim.** District-scale passive survivability during a multi-day outage, with occupant presence
and metabolic gains resolved by household demographics instead of a constant 100 percent, on the
existing dwelling-level no-core geometry. Winter freeze and summer heat arms. Pre-registered
habitability gates (LEED IPpc100, WHO bands, `RT15` F1) scored report-only.

**Why the reports like it.** Every survivability study found assumes constant presence (`RT15` C1 to
C5); the field's own authors name demographic presence as the open question (`RT01` C6). The series
signature survives intact: a frozen-frame EnergyPlus campaign that perturbs only the human term
(`RT11` G1). Inputs are all open (`RT10` F1). Compute is trivial (`RT10` B1, an inference).

**What the engine lacks.** Future or extreme weather ingest, an HVAC-off outage mode, SET and
overheating post-processors, temperature-dependent infiltration (AIM-2, `RT10` E1), and a
presence-response rule for departure during an outage. None exists in OpenUBEM today
(`_scan/scan_openubem_capabilities.md`). Canadian archetypes and districts do not exist either; the
four European districts do, but their EUIs are in restatement (D-EU-107 to 109).

**The occupancy engine.** `RT13` says the raked donor null is the correct product for baseline days.
Use it. This turns the 4J negative result into the 5J input and keeps the LLM out of the paper.

**Blockers.** The infiltration and window-opening objection is answerable by Morris or Sobol screening
across published airtightness ranges (`RT02` G, `RT15` G). Two objections are conceded up front:
evacuation behaviour cannot be validated, and the result covers dense urban stock only (`RT11` G2).

**Risk the reports underplay.** `RT15` C4 cites a Concordia paper on MURB winter-outage resilience
(Baba et al. 2022, *Journal of Building Engineering*), and `RT09` E4 lists an NSERC-funded project on
"passive thermal resilience of high-density Canadian housing under extended winter power outages". If
both are real, the winter arm is already occupied in our own city. The unclaimed part is the
demographic presence term and the district scale, not the outage physics. Verify before choosing.

### Idea 2. Who is home during the heat (`A2`, with `A6` as the equity lens)

**The claim.** Stock-scale indoor heat exposure where presence responds to heat and differs by
demographic group, on the same geometry and weather stack as idea 1, with HVAC status as a variable.

**Why the reports like it.** Three independent `NOT FOUND` results for heat-responsive presence
(`RT04`, `RT05`, `RT08`). Vulnerability indices in Montreal, Toronto, the CDC and UKHSA contain no
indoor physics and no time at home (`RT05` F2, `RT08` F1). Heat deaths are indoor deaths (`RT08` B1,
B2, as reported).

**What it lacks.** The same engine additions as idea 1 plus TM59 and IOD post-processors (`RT05` E).
Its validation blocker is harder: no stock model anywhere has validated indoor temperatures
dwelling by dwelling (`RT05` B10), so the output must be framed as a comparative exposure hazard
index (`RT05` E1, `RT08` E). Household-level billing or health linkage is behind CRDCN and is not
a free fallback (`RT10` E2).

**Relation to idea 1.** Ideas 1 and 2 share the geometry, the weather artefacts, the presence module
and the gates. They differ in whether the HVAC is off (outage) or present but unequal (heat with AC
uptake). One paper could carry both arms; two papers would split the same module. `T12` should be
asked whether this is one paper or two.

### Idea 3. Reading permits with abstention, conformal trust on the stock (`A7`)

**The claim.** An open-weight model reads free-text permit descriptions (Montreal and Toronto both
carry a free-text field, `RT17` F), emits a prediction set and abstains when thin; the sets propagate
into per-building energy bounds with finite-sample coverage on the metered subset.

**Why the reports like it.** Zero extraction studies report abstention; zero conformal studies touch a
physics-based UBEM (`RT17` B1, B2). Components exist separately (`RT17` E3). One GPU and about eight
hours (`RT10` B1). Strong for KTH and Schmidt (`RT09` D).

**What it costs.** It drops the frozen-frame EnergyPlus campaign and the occupancy engine; a
*Building and Environment* editor would not recognise it as the series (`RT11` G1). European EPC
registers are structured, so the LLM is redundant outside permit archives (`RT17` G). Ground truth
requires two to three weeks of manual annotation and a retreat to categorical retrofit classes
(`RT10` E3). Conformal coverage collapses under distribution shift between boroughs (`RT17` B7).

### Idea 4. The zoning bias benchmark (`A11`)

**The claim.** Quantify what core-perimeter zoning does to a European residential stock relative to
dwelling-level no-core division: annual totals move little, peak cooling and top-floor overheating
move a lot (`RT06` B8, B9, as reported and with mismatched references, see section 6).

**Why the reports like it.** Zero external data; the engine already holds both partitions in its
history; `RT06` E names it "thesis 1" for any engine-facing paper; `RT02` ranks it fourth.

**What it needs from the author.** The 4J Step 10 record holds a core-era campaign `C1` (archived,
not retracted, not reported) and a no-core campaign `C2` (spec only, waiting on the engine carry-in).
Whether 5J may report `C1` against `C2` is the author's ruling, not the manager's. It also depends on
D-EU-55 and the pending restatement.

### Idea 5. The release protocol as a paper (`A12`)

**The claim.** A short paper for *Journal of Privacy and Confidentiality* or *Scientific Data*: the
pre-registered membership-inference bar, the measured failure, the partial release, and the custodian
rules that make the withholding the correct output (`RT18` E2, G1).

**Why it matters.** Building-energy journals have no privacy bar at all (`RT18` B6); the audit already
exists. `RT18` says a private retraining under DP-SGD is a known dead end on a corpus this size
(`RT18` E1), so the protocol, not a fix, is the contribution. Not a flagship; a companion that costs
about three months (`RT02` D).

### Idea 6. The scenario axis, held (`A4`)

Open at the intersection (`RT14` B2) but reviewers in 2027 will require a hindcast and a full
factorial attribution (`RT14` E1, E2). Five months, compound uncertainty, no fellowship pull beyond
partial. Hold as the natural sequel once ideas 1 or 2 have built the weather stack.

### Idea 7. The 4J write-up as a diagnostic audit (`A3`, not a 5J paper)

`RT13` E1 lists what a publishable negative result needs: the frozen protocol, an acknowledged
standard baseline, an empirical diagnostic of the mechanism (loss mismatch, variance flattening,
prefix attention decay, `RT13` G1), and constructive scope. None of this changes 4J's gate, null or
threshold. The `RT13` "both sides" reading of the null's fairness (`RT13` G2) belongs in 4J's
discussion.

### Ideas the reports close

* `A1` (agentic), `A5` (flexibility), `A10` (mixed-use band as a paper). `A10` goes to the 3J
  revision as an appendix or becomes a short communication (`RT16` E2).
* `A13` (counterfactual shock synthesis) survives only as the one remaining job for the generator
  (`RT13` E2) and carries an objection no asset answers (`RT02` D).
* `A6` and `A8` do not stand alone; they are the equity lens and the Canadian arm of ideas 1 and 2.

---

## 4. Facts that constrain every choice

* **Calendar.** Every 2026 programme deadline (KTH 2026-10-02 and 10-16, Toronto 2026-10-05, NSERC
  2026-10-17, Berkeley 2026-11-01) falls before any 5J preprint can exist, and every programme counts
  only published, accepted or publicly deposited work (`RT09` B3). The autumn 2026 applications rest
  on 1J to 4J and OpenUBEM. 5J serves the 2027 cycle (MSCA 2027 and the next rounds of the others).
  The angle should therefore be chosen on the science and on 2027 fit, not on autumn 2026 deadlines.
* **A single paper cannot serve all five programmes** (`RT09` A, E2). Resilience physics serves
  Berkeley, NSERC and MSCA; algorithmic AI serves KTH and Schmidt. Ideas 1 and 2 sit on one side,
  idea 3 on the other, idea 5 is a short bridge to the AI side.
* **The raked donor null is the occupancy engine** for anything on baseline days (`RT13` E2). The
  fine-tuned LLM is out of 5J unless idea 7 or `A13` is chosen.
* **Corpus access.** MTUS and ATUS are open to a Canadian university; Eurostat HETUS SUF is not;
  Spain's INE file is public; the UK file is under EUL (`RT07` B2 to B5, F). GSS PUMF is public
  (`RT10` F1). Anything derived by resampling public files is releasable; national files that forbid
  redistribution constrain synthetic releases (`RT18` G1).
* **Weather.** PCIC future-shifted files for every CWEC2020 station and Copernicus C3S products are
  redistributable; CCWorldWeatherGen, Meteonorm and WeatherShift are not (`RT05` F1). `pyepwmorph`
  is MIT but the two reports disagree on its repository and version (section 6).
* **Validation reality.** No stock model has validated indoor temperatures dwelling by dwelling
  (`RT05` B10). No UBEM paper reports cross-platform reproducibility (`RT06` B3). Our engine's measured
  two-host stability is therefore rare, and any exposure or survivability claim is comparative.
* **Compute.** Ideas 1, 2 and 4 are CPU jobs in minutes to hours on one node; idea 3 is about eight
  GPU hours (`RT10` B1, all inferences). No angle needs commercial APIs (`RT10` A).
* **Venue.** *Building and Environment* and *Energy and Buildings* for ideas 1 and 2; *Advanced
  Engineering Informatics* for idea 3; both Elsevier journals accept preprints and require a data
  availability statement (`RT11` B2, `RT10` B2).

---

## 5. Where the ideas touch existing work

* Idea 4 (`A11`) draws on the 4J Step 10 campaigns `C1` (core-era, archived, not reported) and `C2`
  (no-core, spec only). Reporting either in 5J is an author ruling.
* Ideas 1 and 2 on the four European districts depend on the engine carry-in and on D-EU-55 and the
  D-EU-107 to 109 restatement. Nothing in this document quotes a district EUI.
* Idea 5 (`A12`) is built from the 4J audit as pre-registered. Nothing in it changes the bar.
* `RT16` E2 suggests using the mixed-use band to defend the 3J four-channel model. That is a 3J
  revision matter and is recorded here only so it is not lost.

---

## 6. Defects found by reading, before the mechanical vetting

These become strikes in the `VETTING_RT<NN>.md` notes and contradictions for `T12`. Each item cites the
row where the defect sits.

**Angle labels drifted (rules 1 and 6).**
* `RT09` Section D relabels the brief's angles: `A1` becomes "Diffusion vs Raked Donor", `A3` becomes
  "Agentic UBEM Auditing", `A4` becomes "Zero-Fitted Occupancy Microdata", `A5` becomes "Multi-Country
  Time-Use Transfer", `A6` becomes "Future EPWs and Indoor Overheating". Only `A2`, `A7`, `A8`, `A9`,
  `A10` match the brief. The fit table is unusable for the five relabelled rows.
* `RT10` and `RT11` describe `A2` as "compound extreme events, building stock vulnerability, and
  energy inequity", which merges the brief's `A2` and `A6`. Their `A2` rows, objections and blockers
  refer to that merged angle.

**Claims about our own work that the brief did not supply (rule 1).**
* `RT13` B2 and D row 1: "4.7x backbone failure in paper 4"; `RT13` G1 row 4: "about 50k training
  diaries". Neither number is in the brief.
* `RT01` C3 attributes a quotation about catastrophic cross-regional transfer failure to our CENTUS
  paper, which did not run a transfer. `RT01` L07 contradicts its own row by saying transfer "remained
  unexecuted".
* `RT09` D2 states that "the doctoral thesis centered on generative occupancy modeling". The brief did
  not describe the thesis.
* `RT09` A and G1 assert that the Berkeley Climate Futures fellowship runs "via the UC President's
  Postdoctoral Fellowship Program" with DEI as a qualifying threshold. The brief described a
  Chancellor's programme. This may be a conflation of two programmes; the URL check decides.
* `RT09` E lists two funded projects per programme, one of which (NSERC, winter outage survivability)
  would bear directly on idea 1. No identifiers are given; unverifiable as written.

**Identifiers that look invented or inconsistent (rule 4).**
* `RT02` C2: arXiv:2407.12345 for Fuchs et al., where `RT01` and `RT03` cite arXiv:2407.21060 for the
  same authors. `RT02` C3: ORNL/TM-2025/1102 "AutoBEM-Agent". `RT03` C08 and C09: systems with no
  author, venue or identifier.
* Kathirgamanathan et al. 2023: DOI ends 121312 in `RT02` C20 and `RT17` H4, but 121650 in `RT17` C6.
  Touzani et al. 2022: 111998 in `RT02` C21 and `RT17` H5, but 108421 in `RT17` C7.
* Sun et al. 2020: `RT02` C27 and `RT15` C3 give 10.1016/j.buildenv.2020.106884, whose stated title
  is a nursing-home study, while `RT15` C3 describes detached, townhouse and apartment archetypes;
  `RT11` cites a different Sun et al. 2020 at 107068.
* `RT15` C5: Baniassadi et al. 2018 at 10.1016/j.buildenv.2018.06.019 is titled (in `RT15`'s own H
  list) as a high-albedo roof study, yet the row describes a grid-outage survivability study.
* `RT05` C6: "10.80/09613218.2016.1222190" is a malformed DOI (10.1080 elsewhere).
* `RT17` C1, C4, C5, C8 and `RT18` F rows 3 to 5 name sources without resolvable identifiers.
* `RT01` L04 and `RT03` C04: BuildOcc (arXiv:2609.02729, Zenodo 10.5281/zenodo.21192895) is dated
  this month and must be resolved before it is cited anywhere.

**Numbers presented as measured that read as invented (rules 3 and 4).**
* `RT06` A and B4, B5: an "audit of 579 UBEM papers" with a 35 / 45 / 18 / under-2 percent validation
  split. The query is given but the classification of 579 papers is not something the tool did.
* `RT06` B8, B9: zoning effects of 2 to 9 percent, 15 to 30 percent and 30 to 70 percent attributed to
  Cerezo Davila et al. 2016 and Dogan and Reinhart 2017, while the H list contains Dogan and Reinhart
  2013 and a Boston workflow paper. These are the load-bearing numbers for idea 4; treat as unknown.
* `RT11` B1: APCs, turnaround weeks and word limits for six journals, all "checked 2026-09-07".
  Turnaround weeks are not published by Elsevier at that precision.
* `RT10` B1: seconds per EnergyPlus run and core-hours are marked `INFERENCE`, correctly; do not
  quote them as measurements.

**Internal contradictions between reports (for `T12`).**
* `pyepwmorph`: `RT05` says version 2.0.0 at `justinfmccarty/pyepwmorph`; `RT10` says 2.0.1 at
  `intelligent-environments-lab/pyepwmorph`.
* Annex 79: `RT04` B2 says it concluded in 2024; `RT01` B3 lists Annex 95 as its 2024 to 2029
  successor; neither opened the Annex 79 closing report.
* Berkeley programme identity: `RT09` (PPFP) against the brief (Chancellor's Climate Futures).
* NSERC rules: `RT09` B9 to B11 say the standalone PDF is discontinued and the thesis-distinctness rule
  is replaced by a location-of-tenure rule; the brief carried the distinctness rule. Both cannot hold.
* `A2` definition: `RT02` and `RT05` use the brief's definition; `RT10` and `RT11` use the merged one.

**Flattering-direction check (rule 7).** Four reports rank `A9` first with maximal scores, and `RT10`
finds every input for `A9` downloadable, every output shippable and compute negligible. `RT02` did rank
`A1` and `A3` low despite the brief's warmth, so the round is not a failure on that control alone. The
`A9` consensus is nevertheless partly inherited (section 1.3) and rests on rows with the defects above
(`RT15` C3 and C5, `RT09` E4). `T12` must ask each report's `A9` rows to survive the CrossRef titles.

---

## 7. Questions only the author can answer

1. May 5J report the 4J Step 10 core-era campaign against the no-core campaign (idea 4)?
2. Is the local MURB winter-outage line (Baba et al. 2022, `RT15` C4) a collaboration or a competitor
   for idea 1, and does that change the season chosen first?
3. Is a pivot that drops the EnergyPlus frozen frame (idea 3) acceptable for the series?
4. Are ideas 1 and 2 one paper with two arms, or two papers?
5. Are the four European districts usable for 5J before the D-EU-107 to 109 restatement closes, or is
   the Canadian arm the first campaign?

---

## 8. What happens next

1. Done 2026-09-07: seventeen vetting notes carry verdicts; README status column updated. Five rounds
   failed (`RT02`, `RT04`, `RT08`, `RT09`, `RT17`). Whether to re-run those five with the CrossRef
   title required beside every DOI, or to let `T12` adjudicate on the twelve that survived, is the
   author's call; the manager recommends re-running `RT02` and `RT09` at least, because the ranking
   and the programme fit have no verified basis without them.
2. Write `T12_contradictions_and_ranking.md` from section 6 and section 1.3, in the 4J `L17` style:
   each contradiction, the row on each side, "do not split the difference", then one ranking of the
   surviving angles under `RT02`'s rule, no new angle.
3. After `RT12` is vetted, write `DECISION_5J_angle.md` and stop.

Nothing in this document decides the paper.
