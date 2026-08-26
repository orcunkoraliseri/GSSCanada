# Step 7 — Constrained generation and schedules. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_07_constrainedGeneration.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN.** All thresholds pre-registered. 🔴 **The line that stood here until 2026-08-22 — *"Nothing
built"* — had been false for eight days.** Corrected rather than quietly replaced, because a status
line nobody maintains is how a reader concludes that a whole step is untouched.

**Built and run as of 2026-08-22 (night):** the grammar (`G7.10` oracle agreement PASS, 0
disagreements on 10,000 strings under the 34-value `COP` alphabet), the Leg-4 rehearsal generation on
all three folds both constrained and unconstrained, the gate battery on generated text
(`gates_step7_leg4_baseline.json`, **12 PASS / 15 FAIL** over scored gates), the schedule emitter and
the schedule gates (🔴 **`G7.19` ADDED 2026-08-26 under `D-S9-3`(a); `G7.13`–`G7.17` and `G7.19` are 6 PASS / 0 FAIL on all three folds, all six seen
falling** — `G7.19` is the phase gate, and it exists because `FINDING 141` passed the other five), and the chaining pre-screen (90 cells).

🔴 **Still genuinely unbuilt:** work item 7.2 (throughput, job `1286208`), the Leg-5 campaign
(job `1286209`), the untuned-base arm of `G7.7`, the rejection-sampled control at the size `G7.9`
needs, and `G7.18`'s verdict — all of which need a GPU. **Open decision 14 is OPEN.** 🟢 **CORRECTED 2026-08-25 (night): `G7.18` needed EnergyPlus, not a GPU, and it RAN in Step 8 — 9,000 runs, `FINDING 136`, trigger not approached. THE AUTHOR RULED DECISION 14 CLOSED the same night: `independent`, seed 1, with the empirical null as the deliverable. The four items above still need a GPU; decision 14 does not.**

⚪ Everything Leg-4 carries the provenance `LEG-4 PILOT -- NOT REPORTABLE`: the backbone is
`allenai/OLMo-2-0425-1B`, not the reported `Olmo-3-1025-7B`. **No Leg-4 number is a result.**

---

## WHAT THIS STEP MUST PROVE

Two things that are easy to confuse, and the confusion is the failure:

1. **The output is structurally valid.** Trivially true after masking, and therefore nearly worthless
   as evidence about the model.
2. **The masking did not do all the work, and did not do it unevenly.** This is the part that carries
   information, and it is why the firing rate is a headline number rather than a diagnostic.

---

## TIER 3 GATES — STRUCTURAL VALIDITY

| ID | Check | Target | Provenance |
|---|---|---|---|
| **G7.1** | Episode durations sum to 1440 | **100 %**, enforced by the 145-state tally automaton | `RL12`, derived |
| **G7.2** | All codes inside the coding list | **100 %**, against an alphabet of **159**<br>🟢 **RULED 2026-08-20, item 10 (a): the `ACT` alphabet IS the 158 `activity_target_list.csv` codes ∪ `{000}` = 159**, and `G7.2`, `G7.10` and the grammar construction all read it that way. 🟢 **Re-derived from the shipped file: 158 rows, 158 distinct `target_code`s, and `000` is NOT among them** — so a grammar built from that file alone would forbid a code the corpus defines (`FINDING 43`, `D-S3-9`, 8,709 episodes). 🟢 `tools/4thJ_step7_grammar.py` already declares the union in code and its 44-check selftest is green, so this ruling records what the implementation does rather than asking for a change | `RL12` |
| **G7.3** | Transition legality (no workplace-to-home with no travel episode) | **100 %**, encoded as an FSM transition table<br>🔴 **2026-08-20 `FINDING 45`: MEASURED — enforcing this rejects 21,210 of 73,254 real diaries (28.95 %), unevenly by country (ES 43.18 %, UK 24.64 %, IT 23.63 %, a 1.83× spread that `G7.8` cannot see because it stratifies demographically, not by country). And `LOC` has no "workplace" class at all — every non-home, non-transport place is `other_place`. 🟢 **`D-S7-2` RULED (a) BY THE AUTHOR 2026-08-20, BEFORE ANY DIARY WAS GENERATED: the travel requirement is NOT enforced by the grammar and `G7.3` becomes a REPORTED RATE, not a 100 % structural constraint.** The operative `TransitionPolicy` is `PERMISSIVE`; `REQUIRE_TRAVEL` survives in `tools/4thJ_step7_grammar.py` only as the falsifier the selftest uses to prove the constraint has teeth, behind an `acknowledge_finding_45` guard so it can never become operative by accident. 🔴 The corpus baselines (ES 43.18 %, UK 24.64 %, IT 23.63 %, all 28.95 %) are what the generated rate is reported against, and the inherited under-reporting of short trips is a declared limitation next to the Step 9 transport-energy caveat.** | `RL12` |
| **G7.4** | Co-presence consistent with the conditioning household | **100 %**, via pre-compiled grammar variants indexed by household type | `RL02` + `RL12` |
| **G7.5** | 🔴 **Unconstrained well-formedness, before any masking** | ≥ **99.90 %** — **this one measures the model** | **project-chosen** |
| **G7.6** | Round-trip through the Step 3 decoder | 100 % of generated strings decode to a valid diary structure | derived |

🔴 **G7.1 to G7.4 cannot fail while the mask is on.** They are enforcement confirmations, not
measurements. Quoting them as evidence of model quality is the single most likely misreading of this
step, and the parent document says so in the same words.

---

## THE GATES THAT ACTUALLY MEASURE SOMETHING

| ID | Check | Target |
|---|---|---|
| **G7.7** 🔴 Constraint-firing rate, **per demographic stratum** | How often the mask had to intervene | **Reported, not thresholded.** Expect **> 35 %** on the untuned base model (control 1) and **< 2 %** on the fine-tuned model. A high rate with perfect validity means the harness did the work |
| **G7.8** 🔴 Firing-rate **evenness** across strata | The mask propping up minority strata | The ratio of the highest stratum firing rate to the population rate must be **< 3.0**. Above that, the mask is doing most work exactly where the model is weakest and **those strata are biased** |
| **G7.9** Renormalisation audit | Masking shifting the distribution | Level-1 marginals of the constrained batch vs the **unconstrained rejection-sampled control** must agree within **±5 min/day** per category |
| **G7.10** Oracle agreement | A grammar bug | The hand-written `LogitsProcessor` oracle and XGrammar accept/reject **identically** on 10,000 sampled strings, including deliberately malformed ones |
| **G7.11** No silent discard | 🔴 Population bias by attrition | The count of generated records **equals** the count of synthetic persons. Any discarded record is itemised with a reason; unexplained discards: **0** |
| **G7.12** Throughput recorded | An unsized campaign | `throughput_comparison.md` exists, covers both backbones, and reports diaries/second **and** peak KV memory |

---

## SCHEDULE-PRODUCTION GATES

| ID | Check | Target |
|---|---|---|
| **G7.13** | Indoor rule applied | 🟢 **RULED 2026-08-20, item 9 (a):** presence is derived via **`(LOC == "at_home") AND (ACT not in OUTDOOR_AT_HOME)`**, reading the **shipped** exclusion list from Step 2, not a copy. The old form `(LOC == 11)` compared a string against an integer, was silently always `False`, and made presence identically zero for every occupant of every dwelling (`FINDING 42`). 🟢 **Checked against the corpus: `loc_class` has exactly four values — `at_home`, `other_place`, `private_transport`, `public_transport` — and the rule reproduces the shipped `indoor_presence` column on all 2,022,141 episodes that carry an activity: 1,352,977 indoor, and the 10,436 at-home-but-outdoor episodes are exactly `322`, `341`, `342`, `344`.** 🔴 **It differs on 1,927 at-home episodes whose `act` is NULL (ES 290 / IT 105 / UK 1,532), where the shipped column is itself `NA` and the rule returns PRESENT.** In generated text that case arrives as `000`, which `D-S7-1 (c)` made its own state, and a person at home doing an unrecorded activity is present — so PRESENT is the right reading, but it is a reading, and it is written down here rather than left to the `not in` operator. No threshold moved 🟢 **BUILT 2026-08-21** — `tools/4thJ_step7_indoor.py`, selftest **36/36 green**. `V7.c` enforced by re-reading the shipped list and refusing a caller set that differs by one code (both directions tested). `FINDING 42`'s signature is a vacuity guard: a CONSTANT presence signal (all-absent or all-present) FAILs, and the selftest reproduces the old `LOC == 11` form matching **0 of 9** episodes. 🔴 **Never run against real records** — the corpus figures above are the 2026-08-20 measurement, quoted, not re-derived |
| **G7.14** | `Schedule:File` used, not `Schedule:Compact` | Asserted by parsing the emitted IDF fragments |
| **G7.15** | 🔴 `Interpolate to Timestep = No` | Asserted per schedule object. A step-wise presence signal interpolated linearly invents fractional occupants and smears appliance peaks |
| **G7.16** | Schedule length and resolution | 8,760 h × the declared timestep, no gaps, no duplicated timestamps |
| **G7.17** | Presence range | All values in [0, 1]; occupant counts integral where the `People` object expects them |
| 🔴 **G7.19** | **The emitted schedule is on the clock EnergyPlus reads it on** | 🔴 **ADDED 2026-08-26 under `D-S9-3`(a), because `FINDING 141` showed that no gate in Steps 7 or 8 could see a schedule that was four hours out of phase.** `D-S2-5` put every diary on a **04:00** origin; `Schedule:File` has no origin field and EnergyPlus reads value 0 as MIDNIGHT. Every check the board already carried — 8,760 values, `Interpolate to Timestep = No`, `Minutes per Item`, values in [0, 1], the multiplier rebuilt from the artefact — **is true of a series rotated by four hours**. Three arms, all scored on the mean hour-of-day profile of the bundle: **(a)** mean presence at **05:00** is at least **0.90** of the schedule's **own** daily maximum — self-referenced, so it cannot be met by rescaling; **(b)** the daily **trough** falls at **08:00 or later**; **(c)** the manifest **declares** `rotated_to_midnight`, because an artefact that cannot say which clock it is on cannot be validated against one. Registered 2026-08-26: `G7_19_NIGHT_HOUR = 5`, `G7_19_NIGHT_RATIO_MIN = 0.90`, `G7_19_MIN_TROUGH_HOUR = 8`. 🔴 **The per-dwelling counts are a DIAGNOSTIC and carry no verdict**, and that is a specification decision taken before the gate returned one: both arms are POPULATION statements, one household that leaves for work together legitimately has its trough at 07:00, and scoring a stock claim per dwelling would have failed **11 of 100 correct** schedules. The answer to that is the right statement, never a looser number |

---

## 🔴 OPEN DECISION 14 IS A VALIDATION GATE, NOT A DESIGN NOTE

**G7.18 — the chaining-rule sensitivity.** Three rules — independent daily resampling, static
repetition, Markovian habit-coupled — over 100 households and one archetype, scored on annual peak
electrical power and heating/cooling ramp rates.

* **Reported, not thresholded**, with one escalation trigger: 🔴 **if peak demand differs by more than
  25 % between rules, the chaining method dominates the downstream result** and Steps 8 and 9 are
  measuring our schedule-assembly convention rather than the model.
* **Requirement: each rule is run with at least 5 seeds.** A single realisation per rule is a curve
  with no error bar, therefore no way to be wrong, therefore no way to fail — and it always produces
  a winner.
* If the spread across seeds within a rule exceeds the spread between rules, **the experiment has told
  us nothing about chaining**, and the deliverable is that finding, not a chosen rule.

---

## EVERY GATE MUST BE SEEN FAILING

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Disable the tally automaton | G7.1 | G7.2 |
| Add one out-of-list `ACT` to the grammar's allowed set | G7.2 | G7.1 |
| Remove the travel-episode requirement from the FSM | G7.3 | G7.1 |
| Use the wrong household grammar variant | G7.4 | G7.1 |
| Score the **untuned base** model unconstrained | **G7.5** | G7.1 (the mask is off, so state that G7.1 is N/A rather than passing) |
| Concentrate 90 % of firing in one stratum | **G7.8** | G7.7 (the population rate can be unchanged — that is exactly why G7.8 exists separately) |
| Shift the mask to forbid a common activity | G7.9 | G7.1 |
| Introduce an off-by-one in the oracle | G7.10 | G7.1 |
| Silently drop 1 % of records | **G7.11** | G7.1 |
| Set `Interpolate to Timestep = Yes` | G7.15 | G7.14 |
| Emit 8,759 hours | G7.16 | G7.17 |
| Use a **local copy** of `OUTDOOR_AT_HOME` that differs by one code | **G7.13** | G7.17 |
| 🔴 **ADDED 2026-08-22** — emit `Schedule:Compact` instead of `Schedule:File` | **G7.14** | G7.16 |
| 🔴 **ADDED 2026-08-22** — shift every presence value by `+0.5` | **G7.17** | G7.14 |
| 🔴 **ADDED 2026-08-26** — emit on the **04:00 diary origin** instead of the clock EnergyPlus reads (`--no-rotate`) | **G7.19** | G7.13, G7.14, G7.15, G7.16, G7.17 |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any passing gate was never made to
fall.** 🔴 **G7.1 to G7.4 will never fall under any perturbation that leaves the mask on. Record them
explicitly as ENFORCEMENT CONFIRMATIONS rather than counting them in a "gates seen failing" tally** —
a tally that includes gates which cannot fail is a tally that is inflating itself.

---

## VACUITY GUARDS

* **V7.a** — G7.7 and G7.8 FAIL, rather than skipping, if fewer than **10 strata** carry ≥ 100
  records.
* **V7.b** — the runner prints record counts, stratum counts, the grammar's state count and the model
  path **before** any verdict.
* **V7.c** — G7.13 **imports** the Step 2 exclusion list from its shipped path. 🔴 A second copy of a
  list drifts invisibly, and validating against the copy validates nothing.
* **V7.d** — G7.11 counts. It never asserts. A hard-coded expected count that stops being true is how
  three separate 3J counts silently inflated.
* **V7.e** — G7.10's oracle set must contain **known-invalid** strings and the oracle must reject
  them. An agreement test run only on valid strings shows two accepters agreeing about acceptance.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** measure diary quality. Structural validity is orthogonal to fidelity: a grammar-
  perfect diary in which everyone sleeps for 24 hours passes every Tier 3 gate. Tiers 1 and 2 own
  that, and they are scored in Steps 4 and 6.
* It does **not** validate the transfer claim. Step 6.
* It does **not** validate the building model. Step 8.
* 🔴 It does **not** establish that the mask is harmless. G7.9 checks **Level-1 marginals** against
  the rejection control. Renormalisation could still be distorting **joint** structure that G7.9 does
  not look at, and the honest statement in the methods is that the audit covers marginals.
* 🔴 It does **not** cover the schedules' *semantic* correctness — that a presence value of 0.4 in a
  given hour means what the building model will assume it means. That is Step 8's interface question
  and it is where 3J's most expensive bug lived.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Eighteen gates, thirteen perturbations, none run.
* 🔴 The most important line in this document is the one saying G7.1 to G7.4 **cannot fail while the
  mask is on**. They will look like four passing structural gates in any summary table. They are four
  confirmations that a constraint we wrote is being applied, and counting them as validation of the
  model is the misreading this step exists to prevent.

### 2026-08-22 (night) — 🟢 **THE SCHEDULE-PRODUCTION GATES ARE SCORED FOR THE FIRST TIME: `G7.13`–`G7.17`, 5 PASS / 0 FAIL ON ALL THREE FOLDS, AND ALL FIVE SEEN FALLING. 🔴 TWO OF THEM HAD NO REGISTERED FALSIFIER AND THE TABLE ABOVE NOW CARRIES THE TWO THAT WERE ADDED.**

Full implementation record: `4thJ_07_schedules_and_chaining_IMP.md`. Artefacts:
`outputs_step7/schedules/`, `outputs_step7/gates_step7_schedules_baseline.json`,
`outputs_step7/gates_step7_schedules_perturbations.json`.

Everything below is scored on emitted schedules re-read **from disk** — the `.idf` as text and every
`.csv` as text, never from the emitter's in-memory objects. That is `G8.12`'s rule borrowed one step
early, and it is the reason this board is evidence rather than a tautology.

| | `es` | `uk` | `it` |
|---|---|---|---|
| `G7.13` indoor rule, on the **emitted** signal | PASS | PASS | PASS |
| `G7.14` `Schedule:File`, not `Schedule:Compact` | PASS | PASS | PASS |
| `G7.15` `Interpolate to Timestep = No`, **per object** | PASS | PASS | PASS |
| `G7.16` length and resolution | PASS | PASS | PASS |
| `G7.17` presence range and integral head-count | PASS | PASS | PASS |

100 `Schedule:File` + 100 `People` objects and 100 CSVs of 8,760 hourly values per cell; exclusion
list md5 `679518c7f626bd5d408adc96b5a1ff43`, read live from Step 2's shipped path on all three folds.

#### 🟢 The board's first run was a FAIL, and it was right

`G7.13` refused the first baseline: *"the manifest does not record WHICH exclusion list produced this
signal."* True — the emitter recorded the list's md5 but not whether the list used **was** the shipped
one, so `V7.c` could not be checked from the artefact at all. Fixed additively, re-emitted, PASS.

#### 🔴 `FINDING 95` — `G7.14` and `G7.17` were unfalsifiable as registered

The perturbation table listed both **only** in the "must stay clean" column. Under this document's own
coverage clause — *"FAIL the probe if any passing gate was never made to fall"* — the board would have
read four of four with two gates that no registered perturbation could ever fell. Two falsifiers are
added above, marked as additions. All six perturbations run; each felled its gate with the intended
message; the null perturbation felled nothing.

⚪ Declared collateral: the `Schedule:Compact` perturbation **also** fells `G7.15`, because a Compact
object carries no `Interpolate to Timestep` field and `G7.15` correctly reports that the setting was
never asserted. `G7.16` is therefore named as its clean partner. A perturbation that fells two gates
is fine; one whose second casualty is undeclared is not.

#### 🔴 `G7.18` IS NOT EVALUATED, AND OPEN DECISION 14 IS STILL OPEN

The chaining experiment's CPU half ran — three rules over a six-point persistence sweep, 5 seeds,
100 households, 3 folds, 90 cells — and returned **this document's own pre-registered null**:

> *"If the spread across seeds within a rule exceeds the spread between rules, the experiment has told
> us nothing about chaining, and the deliverable is that finding, not a chosen rule."*

On the coincidence metrics that a peak-demand pre-screen is made of, seed noise wins:
`mean_pair_corr` on all three folds (ratios 0.39 / 0.19 / 0.19), `annual_mean` on all three,
`max_ramp` on two of three. `peak_aggregate` and `p99_aggregate` are **degenerate** on `es` and `it`,
pinned at exactly 1.000 in all 30 cells. The rule effect is enormous on monthly activity vocabulary
(ratios 18.17 / 11.89 / 18.36) and on same-day-type adjacent Jaccard (71.64 / 64.50 / 63.77).

🔴 **`G7.18`'s escalation trigger is defined on peak DEMAND and `RL21`'s second metric on annual
heating/cooling ENERGY. Both are EnergyPlus outputs. Nothing in the run above is a watt**, and no
number from it may be substituted for the trigger.

#### 🔴 `FINDING 96` — the vocabulary criterion has no reference, and the reference it does have is flat

`ISTAT gives every respondent exactly ONE diary day, and so does Spain.` Only the UK has a second day
(7,920 persons), and in 99.7 % of those the two days are a weekday and a **weekend** day. So *"the
realistic value computed on the held ISTAT data"* cannot be computed. The anchors that exist are
codes-per-day (es 10.910 / it 11.543 / uk 12.546) and the UK two-day step: **4.907** new codes, union
17.690, Jaccard **0.4325**. 🔴 And the simulated quantity that anchor measures — Jaccard between
adjacent days of **different** day types — moves by **0.003 / 0.001 / 0.002** across all six chaining
rules. The one empirically anchorable criterion cannot tell the rules apart.

#### What this entry does NOT establish

* Not that the schedules are **right**. A dwelling whose occupant sleeps 24 hours a day passes all
  five gates. Structural validity is orthogonal to fidelity, which is this document's opening claim.
* Not DoD item 7 for the reported model. Every diary above is `LEG-4 PILOT -- NOT REPORTABLE`, from
  `allenai/OLMo-2-0425-1B`.
* Nothing about EnergyPlus. No IDF has been run and `Schedule:File` has never been resolved by the
  engine; `G8.12` and `G8.13` are Step 8's and remain unrun.

---

### 2026-08-22 (night, fourth entry) — 🔴 **`G7.12` WAS SCORED AGAINST A REAL ARTEFACT FOR THE FIRST TIME AND FAILED. THAT IS THE CORRECT VERDICT.**

Job `1286208` returned `outputs_step7/throughput_comparison.md`. Scored clause by clause:

| clause | verdict |
|---|---|
| the file exists | 🟢 PASS |
| covers **both** backbones | 🟢 PASS — `allenai/Olmo-3-1025-7B` and `Qwen/Qwen2.5-7B`, one job, one prompt set |
| reports **diaries/second** | 🟢 PASS — 22.5331 vs 26.9839, measured |
| reports **peak KV memory** | 🔴 **FAIL — no valid value exists** |

The fourth clause fails on two independent grounds, either of which is sufficient. The derived pool is
**227.141 GiB** against a physical **74.506 GiB** card — **3.05x the whole GPU** — because the emitter
derives bytes/token from `num_hidden_layers` and OLMo 3 is hybrid (**24 `sliding_attention` layers at
window 4096, 8 `full_attention`**); corrected to the 8 full layers it is **56.785 GiB**, within
**1.135 GiB of Qwen's 55.650**. And `torch_peak_allocated_gib` is **0.0 in both rows**, a structurally
null field rather than a small one, because vLLM v1 runs the model in a worker process.

🔴 **`G7.12` therefore stays FAIL on all three folds.** This is the first Step 7 gate to fail on a
defect **in its own input artefact** rather than on a missing one, and it is exactly what a gate
pointed at a quantity is for. See `FINDING 97` in `4thJ_07_schedules_and_chaining_IMP.md`. Nothing is
re-registered and no threshold moves: the gate's wording was already right.

### 2026-08-26 (early) — 🔴 **`G7.19` IS ADDED, AND IT IS THE FIRST GATE IN THIS STEP THAT CAN SEE WHAT CLOCK A SCHEDULE IS ON. THE BOARD IS 6 PASS / 0 FAIL ON ALL THREE FOLDS AND ALL SIX HAVE BEEN SEEN FALLING.**

Under `D-S9-3`(a), ruled by the author the same day on `FINDING 141`.

🔴 **The reason this gate exists is that the whole existing board passed on the defect.** Step
9 measured a UK hot-water peak at 03:00 and asked what index 0 of the series meant. `D-S2-5` had put
every diary on a **04:00** origin; `Schedule:File` has no origin field and EnergyPlus reads value 0 as
**midnight**. So every schedule this step emitted — and every one of the **13,108 EnergyPlus runs**
Step 8 reported — applied occupancy **four hours early**. `G7.13` through `G7.17` check the exclusion
rule, the object type, `Interpolate to Timestep`, the length, the resolution and the range. **Every
one of those is true of a series rotated by four hours.**

| | baseline `es` | `uk` | `it` |
|---|---|---|---|
| `G7.13` indoor rule on the emitted signal | PASS | PASS | PASS |
| `G7.14` `Schedule:File`, not `Schedule:Compact` | PASS | PASS | PASS |
| `G7.15` `Interpolate to Timestep = No` | PASS | PASS | PASS |
| `G7.16` length and resolution | PASS | PASS | PASS |
| `G7.17` range and integral head-count | PASS | PASS | PASS |
| 🔴 **`G7.19` phase** | **PASS** | **PASS** | **PASS** |
| mean presence at 05:00, as a share of the bundle's own daily maximum | **0.9998** | **0.9979** | **0.9498** |
| hour of the daily trough | **11:00** | **11:00** | **13:00** |

**The same three bundles before the rotation**: 0.674 / 0.787 / 0.767 and troughs at **07:00 / 07:00 /
09:00**. The registered band, 0.90, sits inside that gap and was fixed before either side was scored.

🔴 **The perturbation battery is 7 of 7, and the new one is an ARTEFACT, not a one-off.** The
emitter carries `--no-rotate`, so `outputs_step7/schedules/perturb_norotate/` is a bundle anyone can
rebuild and re-score. It fells `G7.19` on all four of its arms and leaves `G7.13`-`G7.17` clean, which
is the whole claim of `FINDING 141` stated as a test.

| perturbation | fells | clean |
|---|---|---|
| null | **nothing** | everything |
| `Interpolate to Timestep = Yes` | `G7.15` | `G7.14`, `G7.19` |
| emit 8,759 hours | `G7.16` | `G7.17` |
| local copy of `OUTDOOR_AT_HOME` | `G7.13` | `G7.17`, `G7.19` |
| emit `Schedule:Compact` | `G7.14`, `G7.15` | `G7.16` |
| shift every value by +0.5 | `G7.17` | `G7.14`, `G7.19` |
| 🔴 **emit on the 04:00 diary origin** | **`G7.19`** | `G7.13`-`G7.17` |

⚪ `Schedule:Compact` also fells `G7.15`, as it has since 2026-08-22 — a Compact object carries no
interpolate field, so the setting genuinely was never asserted. Declared, not tidied away.

🔴 **The per-dwelling arms carry NO VERDICT and that is a specification decision, not a
loosened band.** Both arms are POPULATION statements. One household that leaves for work together has
its occupancy trough at exactly 07:00, and a night-shift dwelling is legitimately empty at 05:00.
Scored per dwelling the gate would have failed **11 of 100 CORRECT** `es` schedules. The answer to
that is the right statement, never a looser number — the counts are printed beside the verdict as a
diagnostic (`es` night 0/100 trough 11/100, `uk` 0/100 and 0/100, `it` 8/100 and 6/100).

### 2026-08-26 (morning) — 🟢 **WORK ITEM 7.5 IS SCORED AT ITS REGISTERED SIZE. THE PARITY CLAUSE IS DISCHARGED ON ALL THREE FOLDS, AND `G7.9` STILL FAILS 3/3 — WHICH IS THE POINT.**

Jobs `1287231` / `1287232` / `1287233`, all `COMPLETED 0:0` (6:28:40 / 1:28:13 / 3:01:28). The
unconstrained control now carries **75,531 / 16,795 / 48,809 draws** — `FINDING 106`'s re-sizing,
delivered to the record. Scored artefact `outputs_step7/gates_step7_leg5_baseline.json`; the
5,200-draw predecessor is kept beside it as `.bak_prerescore` (18,226 bytes, verified non-empty
before the overwrite). The three `*.bak_5200` files on Speed are untouched.

**Board over scored gates: 21 PASS / 6 FAIL** (was 20 / 7). Exactly one verdict moved.

#### 1. `G7.9` — what the re-size was for

🔴 **The caveat is gone from all three folds and the FAIL is not.** At 5,200 draws every fold's
`G7.9` carried a second reason — *"the control carries N valid diaries against 5200 constrained ones.
A marginal estimated from N diaries cannot resolve 5.0 min/day, so this verdict is about the CONTROL,
not about the mask."* At the registered size that reason is **absent on `es`, `uk` and `it`**. The
only reason left is the deviation itself.

| | `es` | `uk` | `it` |
|---|---|---|---|
| valid control diaries, was → now | 358 → **5,169** | 1,610 → **5,066** | 554 → **5,065** |
| worst category | `111` | `011` | `011` |
| worst deviation min/day, was → now | −103.65 → **−101.02** | −25.39 → **−29.60** | −52.64 → **−48.87** |
| verdict | FAIL | FAIL | FAIL |

🔴 **The deviations barely moved under a 14×/10×/9× increase in the control's sample** (−2.6, +4.2,
−3.8 min/day). The mask genuinely displaces the marginals; it was never the small-sample artefact the
parity clause was written to rule out. **`G7.9` may now be quoted as a statement about the mask.**

#### 2. 🔴 `FINDING 150` — parity was sized off a yield measured at 5,200, and the yield falls at scale

None of the three folds actually reaches parity: **5,169 / 5,066 / 5,065 valid against 5,200
constrained**, short by **31 / 134 / 135**. The cause is measured, not guessed — the validity yield
is lower at the registered size than the 5,200-draw batch it was sized from:

| | `es` | `uk` | `it` |
|---|---|---|---|
| yield, 5,200-draw estimate | 0.068846 | 0.309615 | 0.106538 |
| yield, at registered size | **0.068435** | **0.301637** | **0.103772** |
| draws implied for parity, then | 75,531 | 16,795 | 48,809 |
| draws implied for parity, **now** | **75,984** | **17,239** | **50,110** |

⚪ The shortfall is 0.6 / 2.6 / 2.6 % and the gate does not raise it, so nothing is re-run for it —
but **`implied_draws_for_parity` is a moving target and must not be quoted as a fixed requirement**.
A campaign sized from a yield estimate chases its own tail; the honest statement is a yield with a
sample size attached.

#### 3. 🟢 `V7.a` on `uk` is settled — `G7.7`/`G7.8` were FAILing for want of sample

The one verdict that moved. `uk` carried **9** strata with ≥ 100 records against a floor of **10**;
at 16,795 draws it carries **54**, `v7a_satisfied` is true and both gates PASS.

| | `es` | `uk` | `it` |
|---|---|---|---|
| strata ≥ 100 records, was → now | 10 → **149** | **9 → 54** | 11 → **108** |
| population firing rate, was → now | 0.931154 → 0.931565 | 0.690385 → **0.698363** | 0.893462 → 0.896228 |
| evenness ratio (max 3.0) | 1.0739 → 1.0735 | 1.3593 → **1.4319** | 1.1192 → 1.1158 |
| `G7.7`/`G7.8` | PASS | **FAIL → PASS** | PASS |

🔴 **The estimate itself was never in doubt — the density floor was.** The population firing rate
moves by **0.04 / 0.80 / 0.28 pp** under a 14×/3×/9× sample increase, so `V7.a` was not protecting
against a wrong number; it was refusing to certify evenness computed over cells of size 3. It was
right to refuse and it is right to stop refusing. ⚪ `uk`'s evenness ratio rose 1.3593 → 1.4319 while
passing — the denser measurement is the *less* even one, and it is still well inside the 3.0 band.

#### 4. ⚪ `G7.5` is confirmed, not merely re-observed

FAIL 3/3, unchanged, and now on 6.6× the evidence: **6.84 / 30.16 / 10.38 %** valid against a target
of 99.90 % (was 6.88 / 30.96 / 10.65 %). The rate is stable to **0.04 / 0.80 / 0.28 pp**, so the
free-generation validity rate is a property of the model, not of the batch. 🔴 `G7.5` and `G7.9`
remain **the same failure** — `G7.9`'s control *is* `G7.5`'s valid subset — and the re-size does not
change that.

⚪ Not re-run and not affected: `G7.1`–`G7.4`, `G7.6`, `G7.10`–`G7.13` all hold their prior verdicts.
`G7.3` is REPORTED, not scored, per `D-S7-2` (a).
