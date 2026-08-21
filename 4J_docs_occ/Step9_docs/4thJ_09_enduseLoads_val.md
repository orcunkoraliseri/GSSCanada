# Step 9 — Activity-driven end-use loads. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_09_enduseLoads.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`

---

## STATUS

**OPEN. Nothing built.** All thresholds pre-registered.

---

## WHAT THIS STEP MUST PROVE

That the appliance loads are **adapted from a validated lineage rather than invented**, and that they
are only claimed at the scale that lineage supports.

The technical gates below are the easy half. The provenance gates are the half that decides whether a
reviewer accepts the step at all.

---

## PROVENANCE GATES — THE ONES THAT MATTER MOST

| ID | What it detects | Threshold | Provenance |
|---|---|---|---|
| **G9.1** 🔴 Mapping citation completeness | An invented heuristic wearing a citation's clothes | **100 %** of rows in `activity_appliance_map.csv` carry a source model **and** the specific table or figure the value came from. A row citing only a paper is not cited | **project-chosen** |
| **G9.2** 🔴 VALIDATED labelling | A caveat presented as a method | **100 %** of rows carry VALIDATED or NOT VALIDATED **and** the validation scale. 🔴 **A row labelled VALIDATED with no scale is a FAIL, not a warning** | `RL13` |
| **G9.3** Unsourced-row honesty | A plausible number filling a gap | Every NOT VALIDATED row carries our written reasoning. Count of rows with neither a citation nor reasoning: **0** | **project-chosen** |
| **G9.4** Citation correctness | The Widén conflation, and its siblings | Every cited DOI resolves to the title it is cited under. 🔴 `RL08` gave Widén & Wäckelgård 2010 as *Applied Energy* 87(3):780-789; the correct entry is **87(6):1880-1892**, and 41(7):780-788 is the **different** 2009 lighting paper<br>🔴 **CORRECTED 2026-08-20, `FINDING 47`: this example was WRONG on three counts. `41(7):780-788` names no real paper; `41(7):781-789` is **RICHARDSON** et al. *Domestic lighting*; the real Widen lighting paper is **41(10):1001-1012** (`10.1016/j.enbuild.2009.05.002`); the Widen 2009 paper Step 9 needs is **41(7):753-768** (`10.1016/j.enbuild.2009.02.013`). `RL17`'s "CrossRef-verified" DOI `10.1016/j.enbuild.2009.02.006` resolves to *Estimation of passive cooling efficiency for environmental design in Brazil*. 🔴 **AND THE GATE MUST BE WIDENED: a title-only match would have PASSED our wrong note, because it carried no DOI. `G9.4` must also match volume, issue, page range and FIRST AUTHOR against CrossRef.** 🟢 **RULED 2026-08-20, item 12 (a), APPLIED: `G9.4` PASSES only when volume, issue, page range AND first-author surname all match the CrossRef record — never the title alone.** A title-only match is what let our own citation note pass while being wrong on three counts, and what let `RL17`'s "CrossRef-verified" DOI resolve to a passive-cooling paper about Brazil. 🔴 `V9.c` still governs the unreachable case: print `NOT CHECKED`, never `PASS`. | `RL17` A5, ~~verified~~ **FABRICATED — see `FINDING 47`** |

🔴 **G9.2's "no scale is a FAIL" clause exists because of a specific failure shape:** a presence-test
that merely asks *is a label present?* is satisfied by the label. The scale is the content, and a
document that also carries corrections will contain the right *kind* of token in the wrong place.

---

## BEHAVIOURAL GATES

| ID | Check | Target |
|---|---|---|
| **G9.5** | Cycle completion | An appliance triggered near the end of an activity episode **still runs its full rated cycle**. Asserted on synthetic edge cases, not just on the corpus |
| **G9.6** | Trigger rate | Per-appliance daily activation counts within the range the source model reports, per household size |
| **G9.7** | DHW volume | **30 to 50 L/person/day at 60 °C**, population median. Reported per country |
| **G9.8** | DHW event mix | Four-event structure present (short, medium, bath, shower) with the source model's proportions |
| **G9.9** 🔴 DHW **assignment** check | Re-open the saved IDF and assert every `WaterUse:Equipment` object still points at the schedule it was built with. **A value check cannot see a re-pointed object** — in 3J that hid a ×3.028 draw increase across 56 cells with zero violations reported |
| **G9.10** | Energy closure | Σ end-use loads reconciles with the total injected internal gain, within **0.5 %** |
| **G9.11** | 3-digit dependence | The mapping actually **uses** the third digit: the number of distinct ACL codes with distinct appliance rows must exceed the number of distinct 2-digit groups. 🔴 A mapping that resolves only at 2-digit did not need the corpus decision that preserved 3-digit codes, and that should be known. 🟢 **RULED 2026-08-20, item 11 (a): this gate is EXPECTED TO FAIL, and it is allowed to.** `RL25` established that **0 of 4** published end-use models (CREST, Widén, LPG, RAMP) resolve activity at 3 digits, so an appliance mapping sourced from the literature cannot pass it. 🔴 **The band is NOT relaxed** — relaxing a threshold because the answer came out wrong is the one move this project refuses. The failure is recorded as a FAIL and the 3-digit corpus decision is re-justified on **microdata fidelity** instead: the third digit exists in the source, and discarding it to make a gate pass would be discarding data to flatter a number |
| **G9.14** 🔴 Trigger inputs exist in the generated record | A trigger reading a column the generated diaries do not carry | The set of columns the trigger reads at runtime is a **subset** of the columns present in `../Step7_docs/outputs_step7/generated_<country>.parquet`, asserted against the file, not against a schema constant. 🔴 **`act2` is calibration-only and must not appear in this set.** A trigger reading an absent column does not raise — it silently never fires |

---

## SCALE GATES — BOUNDING THE CLAIM

| ID | Check | Target |
|---|---|---|
| **G9.12** | Stock-scale agreement | Aggregate load shape over ≥ 100 dwellings against the source models' published aggregate profiles, **R² ≥ 0.85** |
| **G9.13** 🔴 Per-dwelling non-claim | **No result in any output, table or figure is a per-dwelling prediction.** Asserted by a search over the results artefacts for per-dwelling framing |

**G9.13 is a gate on our own writing, and it is deliberate.** The source models validate at feeder
scale; a figure that shows one dwelling's predicted day invites exactly the claim the literature does
not support.

---

## EVERY GATE MUST BE SEEN FAILING

| Perturbation | Must fail | Must stay clean |
|---|---|---|
| Strip the table reference from one mapping row | **G9.1** | G9.2 |
| Label a row VALIDATED with no scale | **G9.2** | G9.1 |
| Add a row with a number and no source | G9.3 | G9.1 |
| Cite Widén 2010 as 87(3):780-789 | **G9.4** | G9.1 |
| Truncate an appliance cycle at episode end | **G9.5** | G9.6 |
| Double one appliance's trigger probability | G9.6 | G9.5 |
| Scale DHW draw by 2 | G9.7 | G9.8 |
| Collapse the four events into one | G9.8 | G9.7 |
| 🔴 **Re-point one `WaterUse:Equipment` at another schedule, leaving its values untouched** | **G9.9** | G9.7 — *the value check sees nothing, which is the whole point* |
| Drop one end use from the sum | G9.10 | G9.6 |
| Replace the mapping with a 2-digit one | **G9.11** | G9.10 |
| 🔴 **Add `act2` to the trigger's runtime input columns** | **G9.14** | G9.10, G9.6 — *the appliance simply never fires on that rule and every total still reconciles, which is why nothing else sees it* |
| Zero the load on 20 % of dwellings | G9.12 | G9.10 |
| Add a per-dwelling prediction figure | G9.13 | all others |
| 🔴 **Null perturbation: change nothing** | **nothing** | everything |

### Coverage clause

Cross-tab every perturbation against baseline; **FAIL the probe if any passing gate was never made to
fall.**

---

## VACUITY GUARDS

* **V9.a** — the runner FAILs if `activity_appliance_map.csv` has fewer rows than there are distinct
  ACL codes in the corpus that the mapping claims to cover, **and prints the shortfall**.
* **V9.b** — G9.1 to G9.4 print the row count they scanned before any verdict. A provenance check over
  an empty set passes for the wrong reason.
* **V9.c** — G9.4 resolves DOIs live where possible and **prints `NOT CHECKED` rather than passing**
  when it cannot reach the resolver. 🔴 A check that cannot distinguish *found nothing* from *could
  not run* is not a check.
* **V9.d** — G9.13's search must print the files it scanned and FAIL if it scanned fewer than the
  results directory contains. A green check that scanned nothing is decoration.
* **V9.e** — G9.2's presence test keys on the **structured field**, not on the presence of the word.
  A document containing a superseded quotation contains the right kind of token in the wrong place,
  and a naive presence test reads the correction as compliance.

---

## WHAT THIS STEP'S VALIDATION DOES **NOT** COVER

* It does **not** validate the source models themselves. We adapt CREST, Widén, LPG and RAMP; their
  own validation is theirs, and G9.12 checks only that our adaptation reproduces their aggregate
  behaviour.
* It does **not** establish per-dwelling accuracy, and G9.13 exists to stop us implying otherwise.
  **This is limitation E1 and it bounds every downstream energy claim in the paper.**
* It does **not** cover appliance stock ownership rates by country. If Italian and British dwellings
  own different appliances at different rates, that is a **country-level input we do not have**, and
  it is a real gap in a cross-national paper. State it in the methods rather than let G9.12's
  aggregate agreement imply it was handled.
* 🔴 It does **not** separate this step's contribution from the chaining rule (open decision 14). If
  chaining dominates peak demand, appliance-level realism is being measured through a convention that
  moves the answer more than it does.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — validation document created

* Thirteen gates, fourteen perturbations, none run.
* 🔴 G9.11 is unusual and worth keeping: it checks that a **corpus decision taken for this step** was
  worth taking. Author decision 6 preserved 3-digit activity codes partly so that the appliance
  trigger could distinguish laundry from cooking. If the delivered mapping resolves only at 2-digit,
  that decision bought nothing here — and it is better to know that than to assume it.

### 2026-08-14 (second entry) — G9.14, the gate for a rule that fails by staying silent

* **Fourteen gates, fifteen perturbations, none run.**
* 🔴 **G9.14 exists because the failure it catches produces no error and no wrong number.** A trigger
  rule reading `act2`, a column the generated diaries do not carry, does not raise: the appliance
  simply never fires. Energy closure (G9.10) still reconciles, trigger rates (G9.6) still fall inside
  the source model's range for every rule that *did* fire, and the load is missing rather than wrong.
* **It asserts against the file, not against a schema constant.** A schema constant is written by the
  same hand as the trigger and would agree with it about a column neither has checked exists.
