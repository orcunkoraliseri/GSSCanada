# Step 9 — Activity-driven end-use loads

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 9. Validation: `4thJ_09_enduseLoads_val.md`

---

## STATUS

**OPEN. Sourced by `RL13`. Nothing built.**

---

## AIM

This step is the answer to *"why generate 145 activity classes when a building model needs a presence
fraction?"*

**A diary says what people are doing, and that is the signal a presence fraction discards.**

---

## 🔴 DO NOT INVENT THE MAPPING

The strongest single instruction to come out of `RL13`. A validated lineage already exists:

| Model | Reference |
|---|---|
| **CREST** | Richardson et al., 2010 |
| **Widén et al.** | 2009 (lighting), 2010 (activity patterns and electricity demand, *Applied Energy* **87(6)**, 1880-1892) |
| **LoadProfileGenerator** | Pflugradt, 2016 |
| **RAMP** | Lombardi et al., 2020 |

Several are open source. The mechanism is a **two-stage stochastic trigger**: an active time-use code
fires an appliance with probability `P(appliance | activity)`, then a rated power curve and cycle
duration **run to completion**.

**We adapt that logic to the HETUS ACL. We do not author a new heuristic.** An ad-hoc mapping is the
single easiest thing in this paper for a reviewer to reject, and inventing one when four validated
ones exist would be indefensible.

🔴 **Citation note, from the vetting record:** `RL08` gave Widén and Wäckelgård (2010) as
*Applied Energy* 87(3):780-789. That is a conflation with Widén et al. 2009, *Energy and Buildings*
**41(7)**:780-788. `RL06`, `RL13` and `RL17` all give 87(6):1880-1892 for the 2010 paper, and that is
the correct one. **Two distinct real papers; cite each for its own contribution.**

---

## 🔴 THIS STEP IS WHY THE `ACT` FIELD KEPT THREE DIGITS

Author decision 6 fixed one wave per country, so nothing spans the ACL 2000 break and nothing forces
2-digit pooling. **That decision was taken partly for this step.** The appliance trigger needs to
distinguish laundry from cooking from washing from dishwashing; 2-digit codes collapse exactly those
distinctions.

If a future corpus decision reintroduces 2-digit pooling, **this step is the one that loses its
input**, and it should say so loudly at the time rather than quietly degrade.

---

## 🔴 SECONDARY ACTIVITY: THE FIELD THIS STEP WAS PROMISED AND DOES NOT GET. RESOLVED 2026-08-14

Step 3's item 3.2-bis keeps `act2_raw` in the corpus and names **this step** as the reason: an
appliance triggered by an activity that is only ever *secondary* — a television on while eating, a
washing machine running while the respondent does something else — is exactly the load paper 1 got
wrong by construction.

🔴 **But this step does not consume the real corpus. It consumes Step 7's generated diaries, and those
carry no secondary activity at all**, because `act2` is not serialised into the `DUR,ACT,LOC,COP`
tuple. Written down because the two documents were consistent about the field and inconsistent about
who receives it, and the gap is invisible in code: a trigger that reads a column which is simply
absent does not fail, it just never fires.

**The resolution, and it costs the step nothing it actually had:**

* **The trigger fires from the primary code alone**, on generated and real diaries alike. That is also
  what CREST, Widén, LPG and RAMP do — they drive from a single activity stream — so adapting their
  logic unchanged is the *conservative* reading of "do not invent the mapping", not a compromise.
* **`act2` is used where it exists, to estimate the probability rather than to fire it.**
  `P(appliance | primary activity)` is calibrated on the **real** corpus with secondary activity
  visible, so appliance use that respondents recorded as secondary is absorbed into the trigger
  probability instead of being dropped. 🔴 **This is the only place `act2` enters Step 9, and it enters
  as a calibration input, never as a runtime field.**
* **Per country, and only where coverage supports it.** Until `outputs_step3/act2_coverage.md` exists
  with four measured rates, no calibration uses `act2` at all — Step 3's rule that no step conditions
  on it before then applies here without exception.
* 🔴 **The calibration reads SLOTS, not episodes. Added 2026-08-14, from Step 1's measurement.**
  `act2_raw` is stored per episode under a first-of-run rule, and Step 1 measured on Spain that
  **13,009 of 430,754 episodes carry more than one distinct secondary activity and 11,216 mix blank
  with non-blank.** Calibrating from the episode column would therefore estimate the probability from
  a lossy summary of the very stream it is trying to recover. **Step 9 needs a rate, not a timing, and
  the slot-level accounting is the one that has not discarded anything.** Spain: 340,269 of 2,778,480
  slots (12.2 %) is the number this calibration uses; 80,800 of 430,754 episodes (18.8 %) is a
  different quantity and is not interchangeable with it.

**What this costs, stated rather than assumed:** a load whose activity is *always* secondary and never
primary for anyone is invisible to the generated path, and no amount of calibration recovers the
*timing* of such a load — only its rate. That is a real bound on the appliance claim and it belongs in
the methods next to limitation E1.

**If all four countries turn out to record `act2` at a usable rate**, Step 3 may serialise it, and
this step is the reason to. 🔴 **That decision has to be taken before the corpus is emitted**, because
adding a fifth tuple element afterwards invalidates the corpus, the grammar and every trained fold.

---

## DOMESTIC HOT WATER

The load that matters most in a well-insulated dwelling, and **3J found the DHW plant load-bearing in
its energy result.**

* **Jordan and Vajen four-event tapping model**: short draw, medium draw, bath, shower.
* Roughly **30 to 50 L/person/day at 60 °C**.
* Drivers: activity codes for washing, showering, food preparation and laundry.

🔴 **3J's DHW lesson, carried forward:** a transform that re-points a `WaterUse:Equipment` object at a
*different* schedule leaves no before/after pair for a value check to examine. In 3J that hid a
**×3.028** rise in a commercial laundry's draw across all 56 cells while every audit reported zero
violations. **Any DHW transform here needs an assignment check, not only a value check.**

---

## 🔴 THE VALIDATION-SCALE CATCH, WHICH BOUNDS THE WHOLE DOWNSTREAM CLAIM

The published activity-to-load models validate against **aggregate** demand: 100 to 500 dwellings,
feeder or district scale, R² above 0.90. **Individual single-dwelling prediction has high residual
variance**, because when one specific person runs the washing machine is irreducibly stochastic.

**Therefore the downstream claim is about load shapes and distributions across a stock, never about
predicting one household's day.**

Every mapping is labelled **VALIDATED** or **NOT VALIDATED**, with the scale at which it was
validated. **An unvalidated mapping is a caveat, not a method.**

---

## WORK ITEMS

### 9.1 — Build the activity-to-appliance table

One row per (ACL 3-digit code × appliance), carrying:

* `P(appliance | activity)`;
* rated power and cycle duration;
* the **source model** it was adapted from (CREST / Widén / LPG / RAMP);
* the **exact citation and table** it came from;
* a **VALIDATED / NOT VALIDATED** label with the validation scale.

🔴 **Any row we could not source is labelled `NOT VALIDATED` and carries our reasoning. It is never
given a plausible-looking number.**

**Output:** `outputs_step9/activity_appliance_map.csv` + `mapping_provenance.md`.

### 9.2 — Implement the two-stage trigger

Activity fires appliance with probability P; the appliance then runs its rated curve **to completion**,
independently of whether the activity episode ends. That completion behaviour is the part naive
mappings get wrong, and it is what produces realistic load shapes.

### 9.3 — DHW

Jordan and Vajen four-event model, driven from washing, showering, food-preparation and laundry codes.
Per-person volumes recorded, not assumed.

### 9.4 — Emit end-use load profiles

Per dwelling, per timestep, per end use. Injected into the Step 8 IDFs as internal gains and
`WaterUse:Equipment` flows.

### 9.5 — Aggregate and compare

At **stock** scale, which is the only scale the source models validate at. Report distributions and
load shapes, never per-dwelling predictions.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step9/activity_appliance_map.csv` | Step 9 validation; the methods section |
| `outputs_step9/mapping_provenance.md` | The methods section; limitation E1 |
| `outputs_step9/enduse_profiles/*.csv` | Step 8 re-run with loads |
| `outputs_step9/stock_aggregates.csv` | The results section |

---

## HOW IT RUNS

`sbatch`, `ps`, `-t 7-00:00:00`. CPU only.

---

## WHAT BLOCKS THIS STEP

Step 7's diaries (with 3-digit codes intact) and Step 8's archetypes.

---

## DEFINITION OF DONE

1. Mapping table complete, every row cited to a published model and table.
2. Every row labelled VALIDATED or NOT VALIDATED with its validation scale.
3. Two-stage trigger implemented with cycle-to-completion behaviour.
4. DHW implemented with an **assignment** check as well as a value check.
5. Results reported at stock scale only.
6. All Step 9 gates PASS and each has been seen failing.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 The failure mode this step is most exposed to is not technical. It is that a mapping row with no
  source acquires a plausible number during implementation, and by the time anyone audits it, the
  number is in three artefacts and reads as corroborated. **A claim repeated across artefacts is not
  corroborated; it is copied.**

### 2026-08-14 (second entry) — the secondary-activity gap, found between two correct documents

* 🔴 **Step 3 keeps `act2_raw` and names this step as the reason. This step never receives it**, because
  it reads Step 7's generated diaries and `act2` is not serialised. **Neither document was wrong on its
  own**; the gap existed only in the join, and it would have surfaced as an appliance rule that quietly
  never fired.
* **Resolved by demoting the field from a runtime input to a calibration input.** The trigger fires
  from the primary code — the same single-stream design CREST, Widén, LPG and RAMP use — and `act2`
  estimates `P(appliance | primary activity)` on the real corpus so that secondary-recorded appliance
  use is absorbed into the probability rather than lost.
* **`G9.14` added**, asserting the trigger's runtime columns are a subset of what the generated file
  actually carries, and that `act2` is not among them. Its perturbation is adding `act2` to that set:
  the rule stops firing, every energy total still reconciles, and **no other gate moves**.
* **The bound is stated rather than assumed**: a load that is always secondary and never primary for
  anyone is invisible to the generated path, and calibration recovers its rate but not its timing.
  That sits beside limitation E1 in the methods.

### 2026-08-14 (third entry) — the `act2` calibration is pinned to slots, not episodes

Step 1's gate re-run on Spain measured something this step needed. `act2_raw` is stored **per episode**
under a first-of-run rule, and the episode split key does not include the secondary activity, so
**13,009 of 430,754 Spanish episodes carry more than one distinct `ASECU` value and 11,216 mix blank
with non-blank.** Slot-level and episode-level coverage are therefore different quantities: 340,269 of
2,778,480 slots (12.2 %) against 80,800 of 430,754 episodes (18.8 %).

🔴 **The calibration of `P(appliance | primary activity)` reads the slot-level stream.** Calibrating
from the episode column would estimate the probability from a lossy summary of the stream it exists to
recover, and it would do so silently — the number would look right and be systematically wrong in a
direction set by episode length. This step needs a **rate**, not a timing, and the slot accounting has
discarded nothing.

Nothing else changes: `act2` remains a calibration input and never a runtime field, `G9.14` still
asserts it is absent from the generated record, and no calibration uses it at all until
`../Step3_docs/outputs_step3/act2_coverage.md` carries four measured rates — now required on **both**
bases.
