# Step 7 — Constrained generation and schedules. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_07_constrainedGeneration.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing built.** All thresholds pre-registered.

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
| **G7.2** | All codes inside the coding list | **100 %**<br>🔴 **2026-08-20 `FINDING 43`: the alphabet is the 158 `activity_target_list.csv` codes ∪ `{000}` = 159. `000` (D-S3-9, 8,709 episodes) is NOT in that file; a grammar built from it alone would forbid a code the corpus defines.** | `RL12` |
| **G7.3** | Transition legality (no workplace-to-home with no travel episode) | **100 %**, encoded as an FSM transition table<br>🔴 **2026-08-20 `FINDING 45`: MEASURED — enforcing this rejects 21,210 of 73,254 real diaries (28.95 %), unevenly by country (ES 43.18 %, UK 24.64 %, IT 23.63 %, a 1.83× spread that `G7.8` cannot see because it stratifies demographically, not by country). And `LOC` has no "workplace" class at all — every non-home, non-transport place is `other_place`. `D-S7-2` open; recommend (a) drop the travel requirement and report the rate instead.** | `RL12` |
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
| **G7.13** | Indoor rule applied | Presence derived via `(LOC == 11)` 🔴 *(2026-08-20 `FINDING 42`: must be `LOC == "at_home"` — the serialised LOC is a string, `== 11` is silently always False)* `AND (ACT not in OUTDOOR_AT_HOME)`, reading the **shipped** exclusion list from Step 2, not a copy |
| **G7.14** | `Schedule:File` used, not `Schedule:Compact` | Asserted by parsing the emitted IDF fragments |
| **G7.15** | 🔴 `Interpolate to Timestep = No` | Asserted per schedule object. A step-wise presence signal interpolated linearly invents fractional occupants and smears appliance peaks |
| **G7.16** | Schedule length and resolution | 8,760 h × the declared timestep, no gaps, no duplicated timestamps |
| **G7.17** | Presence range | All values in [0, 1]; occupant counts integral where the `People` object expects them |

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
