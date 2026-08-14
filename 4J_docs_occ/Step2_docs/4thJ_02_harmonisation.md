# Step 2 — Harmonisation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 2. Validation: `4thJ_02_harmonisation_val.md`

---

## STATUS

**OPEN. Specified by `RL02`, adjudicated in part by `RL17`. Nothing built.**

---

## AIM

Turn four national episode tables into **one alphabet**: a single activity code list, a single
location code list, a single co-presence representation, a single time grid, one filter rule.

This step is where the paper's premise becomes real or fails quietly. If harmonisation is wrong, the
model learns four dialects and the transfer claim measures our mapping rather than HETUS's.

---

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Source |
|---|---|
| **The `ACT` field keeps 3 digits** | Author decision 6. One wave per country, all four sharing one coding-list generation, so nothing spans the ACL 2000 break |
| Activity coding: 10 major groups, 36 two-digit subdivisions, identical between the 2008 and 2018 editions | `RL02` |
| Location: 10-19 stationary, 20-39 transport, in one field. **11 = Home** | `RL02` |
| Co-presence is **five binary flags**, not one code | `RL02`; corrects our own earlier assumption |
| 🔴 **Location 11 merges dwelling + yard + garden** | `RL02`. Presence in the *conditioned volume* is not recoverable from location alone |
| Indoor rule: `indoor = (LOC == 11) AND (ACT not in {gardening, outdoor construction, ...})` | `RL02`, adopted |
| Filter: age ≥ 11, 04:00 origin, 10-minute grid, per-country diary-days flag | Parent 2C |
| MTUS-69 is the bridge **only** if earlier waves are used in validation | Parent 2D, after decision 6 |

🔴 **The exclusion list in the indoor rule is finalised against the transcribed ACL, never guessed.**
A reviewer who knows HETUS will look for this rule specifically, and an invented exclusion list is
the easiest thing here to reject.

---

## INPUTS

* `../Step1_docs/outputs_step1/episodes_<country>.parquet` — four files
* `../Step1_docs/outputs_step1/codebook_facts_<country>.md` — the only authority on what each field
  means. **Not `RL02`, not `RL17`.** Those are hypotheses; the codebook is the fact.

---

## WORK ITEMS

### 2.1 — Build the activity crosswalk, from the codebooks

One table, four columns of national codes mapping to one target list. Because all four waves share a
coding-list generation, this should be close to the identity map — **and if it is not, that is a
finding about the corpus, not a licence to improvise.**

* Every mapping row carries the codebook page it came from.
* Every code that maps to nothing is **listed**, counted, and either resolved or declared. It is
  never silently dropped.
* 🔴 A one-to-many mapping requires a written rule and is flagged in the output, because a
  one-to-many mapping is where an arbitrary heuristic hides.

**Output:** `outputs_step2/crosswalk_activity.csv` + `crosswalk_unmapped.md`.

### 2.2 — Location crosswalk and the indoor rule

Same discipline. Then implement:

```
indoor_presence = (LOC == 11) AND (ACT not in OUTDOOR_AT_HOME)
```

`OUTDOOR_AT_HOME` is an explicit, versioned list derived from the ACL, stored as data rather than
inline in code, so the validation can read the same list the transform used.

**Output:** `outputs_step2/crosswalk_location.csv`, `outputs_step2/outdoor_at_home.csv`.

### 2.3 — Co-presence normalisation

Five flags: alone / with partner / with children / with other household members / with other persons.

* Countries that record fewer than five get the missing ones as **explicitly missing, never as 0**.
  Zero means "recorded and absent"; missing means "not recorded". Collapsing them destroys exactly
  the field paper 1 identified as the source of load **over**estimation.
* The packed on-wire form is fixed in Step 3, not here.

**Output:** `outputs_step2/copresence_availability.md` — which country records which flag.

### 2.4 — Apply the filter and emit the harmonised table

Age ≥ 11, 04:00 origin, 10-minute grid, per-country `diary_days` flag carried through.

**Output:** `outputs_step2/harmonised.parquet`, one row per episode, plus
`outputs_step2/filter_report.md` counting exactly how many respondents and diaries each filter clause
removed, per country.

🔴 **Count what the filter removed, per clause, per country.** A filter that removes 3 % of Italy and
19 % of France is telling you something about France, and a single total hides it.

---

## OUTPUTS AND INTERFACES

| Artefact | Consumed by |
|---|---|
| `outputs_step2/harmonised.parquet` | Step 3 |
| `outputs_step2/crosswalk_*.csv` | Step 2 validation; the methods section |
| `outputs_step2/outdoor_at_home.csv` | Step 7D (diaries to schedules) and Step 2 validation |
| `outputs_step2/copresence_availability.md` | Step 5, which must not condition on a flag a country never recorded |
| `outputs_step2/filter_report.md` | Step 2 validation gate G2.7 |

---

## HOW IT RUNS

`sbatch`, partition `ps`, `-t 7-00:00:00`. CPU only. No GPU is needed anywhere in this step.

---

## WHAT BLOCKS THIS STEP

Step 1.3 must have emitted all four episode tables.

**What this step blocks:** Steps 3 onward. Also Step 9 — the appliance mapping needs 3-digit codes,
and this is the step that either preserves them or does not.

---

## DEFINITION OF DONE

1. Four crosswalks, every row cited to a codebook page, every unmapped code listed.
2. The indoor rule implemented, its exclusion list stored as data, and the list justified from the ACL.
3. Co-presence availability documented per country, with missing distinguished from absent.
4. `harmonised.parquet` emitted, and the filter report counting removals per clause per country.
5. All Step 2 gates PASS **and each has been seen failing**.

---

## PROGRESS LOG

Append-only.

### 2026-08-14 — step document created

* 🔴 The single most consequential item here is **2.2**. Papers 2 and 3 were built on the assumption
  that presence in the conditioned volume is readable from the location field. `RL02` showed it is
  not, because code 11 merges dwelling, yard and garden. This step is where that correction either
  enters the pipeline or is lost.
* Author decision 6 removed the pressure to harmonise at 2-digit. **Do not reintroduce 2-digit
  pooling for convenience** — Step 9's appliance triggering needs the third digit, and once it is
  gone this step cannot give it back.
