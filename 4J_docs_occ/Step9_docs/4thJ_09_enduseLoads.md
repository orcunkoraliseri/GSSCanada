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
