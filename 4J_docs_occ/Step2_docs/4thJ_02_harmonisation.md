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
| ~~Location: 10-19 stationary, 20-39 transport, in one field.~~ **Retracted — see D-S2-3.** **11 = Home** stands | `RL02`, half of it falsified by the Spanish codebook |
| ~~Co-presence is **five binary flags**~~ **Five is the shared core, not the ceiling — see D-S2-2** | `RL02`, corrected by the Spanish codebook |
| 🔴 **Location 11 merges dwelling + yard + garden** | `RL02`, confirmed on the Spanish file and widened — see D-S2-4 |
| Indoor rule: `indoor = (LOC == 11) AND (ACT not in {gardening, outdoor construction, ...})` | `RL02`, adopted |
| ~~Filter: age ≥ 11, 04:00 origin, 10-minute grid, per-country diary-days flag~~ **Origin is no longer decided — see D-S2-1.** The other three clauses stand | Parent 2C |
| MTUS-69 is the bridge **only** if earlier waves are used in validation | Parent 2D, after decision 6 |

---

## 🔴 DECIDED 2026-08-14, AFTER THE SPANISH FILE

Four manager decisions forced by `../Step1_docs/outputs_step1/codebook_facts_spain.md`, findings
F-ES-1 to F-ES-4. Each one overrides a line that came from `RL02` and was never measured.

### ✅ D-S2-1 is CLOSED, 2026-08-15, as **D-S2-5 below**. The text that follows is kept as the record of why it was reopened; read D-S2-5 for the decided value.

### D-S2-1 — the day origin is **reopened**, and it does not close until all four codebooks are in hand

Spain's diary runs **06:00 to 06:00** (F-ES-1). No 04:00-origin day can be built from it: the two
hours from 04:00 to 06:00 belong to a different calendar day than the one the respondent reported on.

**04:00 is withdrawn as a decided value.** It was `RL02`'s standard, not a measured one, and one of
four countries has already broken it. Choosing the common origin now would mean choosing it from
one country and extending it by assumption, which is the defect this step exists to prevent.

* The origin is chosen **once UK, France and Italy codebooks are transcribed**, from the four measured
  origins, and it is recorded here as a fifth decision at that point.
* Until then no document may state an origin as decided, and **the Spanish reader's native 06:00
  indexing is left untouched** — re-indexing to a value we may not keep would destroy the only
  origin we have measured.
* What is already fixed: the harmonised day is **24 hours of 10-minute slots**, and the origin is a
  single constant shared by all four countries, not a per-country field.

### ✅ D-S2-5 — the day origin is **04:00**, reached by treating each diary as a CYCLIC day. Decided 2026-08-15.

D-S2-1 said the origin is chosen from every measured codebook **or not at all**. Author decision 16
excluded France, so **three is now every country in the corpus** and all three codebooks are in hand.
The measured origins:

| Country | Origin | Source |
|---|---|---|
| Spain | **06:00** | F-ES-1, INE `INTERVALO` 1 = 06:00-06:10 |
| Italy | **04:00** | QUEST-DG p.2, *"il diario inizia alle 4.00 del mattino"* |
| UK | **04:00** | F-UK-5, CTUR p. 2, `tid` 1 = 04:00-04:10 |

🔴 **A shared origin is not a preference, it is a requirement of leave-one-country-out.** If Spanish
days are serialised two hours out of phase with the others, the model learns "the shifted dialect is
Spain" and the transfer claim measures our indexing, not HETUS's. This is the same argument that keeps
country-extra co-presence flags out of `COP` in D-S2-2.

**No re-basing is possible, so the diary is treated as a cyclic 24-hour day.** Spain's respondent never
reported 04:00-06:00 *of the diary's own calendar day*; rotating a 06:00-origin diary to a 04:00 origin
takes those two hours from the **tail of the same diary** — the same respondent's following early
morning. That is a real splice and it is written down as one, not hidden in an index arithmetic.

**Origin = 04:00. Three reasons, in order of weight.**

1. 🔴 **It splices one country instead of two.** Rotating to 06:00 would require the same cyclic move on
   both the UK and Italy; rotating to 04:00 requires it on Spain alone.
2. **The splice lands in the sleep block.** At 04:00-06:00 the overwhelming majority of respondents in
   every one of the three countries are asleep, so the discontinuity falls at the least informative
   point of the day. **This is the whole reason both UK and Italy chose 04:00 natively**, and it is
   HETUS's own guideline origin.
3. Two of three deliveries already use it, so two of three need no transformation at all.

🔴 **Three consequences that must be implemented and checked, not assumed away.**

* **Spain's episode count will change.** The episode straddling 04:00 is split in two by the rotation.
  Spain's 430,754 is a Step 1 quantity pinned by `G1.1`; the Step 2 count is a **different quantity**
  and must be reported as such, exactly the way slot-level and episode-level `act2` counts were kept
  apart. **A Step 2 gate must assert `sum(DUR) == 1440` survives the rotation for 100 % of diaries.**
* **The rotation must be invertible.** The runner keeps the native origin per country as metadata, and
  a round-trip test rotates back and compares to the Step 1 table byte for byte.
* 🔴 **`origin_hour` is metadata, never a serialised field.** A per-country origin column reaching Step
  3 would leak country identity into LOCO by the front door after we closed the back one.
* **The Spanish reader is still not re-indexed.** Rotation happens in Step 2, on the harmonised table,
  where it is visible and testable. Step 1 keeps native indexing per country.

### D-S2-2 — co-presence: **five shared flags, plus country extras kept as named columns**

Spain fields **six** flags — `SOLO`, `PAREJA`, `PADRES`, `MENOR`, `OTMH`, `OTCON` (F-ES-2). The
harmonised schema is:

* **The five HETUS flags stay the shared core**, because they are what the other three cycles are
  expected to field and what makes the countries comparable at all.
* **`PADRES` is kept, as a country-extra column**, named and documented. It is **not** folded into
  "with other household members": that collapse is wrong for exactly the multigenerational household
  the flag marks, and paper 1 names co-presence handling as the source of load overestimation.
* **A flag a country never recorded is explicitly missing, never 0.** Zero is "recorded and absent".
* 🔴 **`MENOR` is not asserted equal to the HETUS "with children" flag.** Spain defines it as *minors
  under 10 living with you*, which is a household-composition test, not a parenthood test. It is
  mapped to the shared flag **with its national definition recorded on the mapping row**, and the
  same test is applied to each of the other three when its codebook arrives. If two countries turn
  out to define that flag differently, the difference is reported, not averaged away.
* Extras are named `cop_extra_<country>_<field>` so that no country's extra can be mistaken for a
  shared flag by a later step.

**Step 5 may not condition on any extra column**, because a country-specific flag cannot be a
conditioning variable in a leave-one-country-out design.

### D-S2-3 — location: **no range filter, anywhere.** Class membership is by explicit crosswalk

`RL02`'s "10-19 stationary, 20-39 transport" is **false for Spain** (F-ES-3). In the Spanish list
`21-29` are places, not transport, and **`41` is public transport** — above the range, and present in
the delivered file. A `10 <= LOC <= 39` filter drops every public-transport episode and mislabels
seven place codes as travel.

* **No step may test a location code by numeric range.** Membership comes from
  `crosswalk_location.csv`, code by code, cited to a codebook page.
* The target classes are **at-home / other place / private transport / public transport**, and
  every national code maps to exactly one, or is listed as unmapped.
* 🔴 **Public transport is a target class in its own right**, not a residue. A crosswalk that
  produces zero public-transport episodes for any country is a failure to be investigated, not a
  finding.
* The same treatment applies to the other three countries: their ranges are **measured, not assumed
  to be Spain's either.**

### D-S2-4 — code `11` is confirmed, and it also carries work-at-home

METH p. 124 defines `11` as house, garage, vegetable plot, garden or grounds attached to the
dwelling, **and states that working from home is coded `11` too** (F-ES-4).

* The indoor rule in 2.2 **stands** and becomes more load-bearing, not less: `LOC` alone cannot
  separate the conditioned volume from the grounds, and the `OUTDOOR_AT_HOME` exclusion list is the
  only thing that does.
* **Work-at-home is not excluded** — it is inside the conditioned volume, so it is indoor presence.
  But it means `LOC == 11` alone cannot tell "at home, not working" from "working at home", and
  **Step 9 needs that distinction for equipment load.** It comes from `ACT`, which is why the third
  digit is kept.
* The exclusion list is finalised **against each transcribed ACL**, and if the four lists disagree on
  which activities are outdoor-at-home, the disagreement is reported.

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

🔴 **The same crosswalk maps `act2_raw`.** Secondary activity is coded in the same national list as
primary activity, so it is harmonised by the same table and **no second crosswalk is built**. A
separate table for the secondary field would be two mappings of one list that can drift apart. The
three states of `act2` — not recorded, recorded and blank, recorded with a value — survive
harmonisation unchanged; **blank is not a code and is never mapped to one.**

### 2.2 — Location crosswalk and the indoor rule

Same discipline, and **per D-S2-3 there is no numeric range test anywhere** — every national code is
mapped explicitly to one of at-home / other place / private transport / public transport, or listed
as unmapped. Then implement:

```
indoor_presence = (LOC == 11) AND (ACT not in OUTDOOR_AT_HOME)
```

`OUTDOOR_AT_HOME` is an explicit, versioned list derived from the ACL, stored as data rather than
inline in code, so the validation can read the same list the transform used. Per D-S2-4, work-at-home
is **not** in that list.

**Output:** `outputs_step2/crosswalk_location.csv`, `outputs_step2/outdoor_at_home.csv`.

🔴 `crosswalk_location.csv` carries an explicit **`target_class`** column holding one of the four
classes. Gate **G2.11** and vacuity guard **V2.e** import that column rather than restating the class
list, so the shipped crosswalk is the single place the classes are defined.

### 2.3 — Co-presence normalisation

Per D-S2-2. Five shared flags — alone / with partner / with children / with other household members /
with other persons — **plus every country-specific extra, kept as its own named column.**

* Countries that record fewer than five get the missing ones as **explicitly missing, never as 0**.
  Zero means "recorded and absent"; missing means "not recorded". Collapsing them destroys exactly
  the field paper 1 identified as the source of load **over**estimation.
* Spain's sixth flag `PADRES` is carried as `cop_extra_es_padres`. It is **not** merged into "other
  household members".
* Every mapping row records the **national definition** of the flag it maps, not just its name.
* The packed on-wire form is fixed in Step 3, not here.

**Output:** `outputs_step2/copresence_availability.md` — which country records which flag, which
extras exist, and how each national definition differs from the shared flag it maps to.

### 2.4 — Apply the filter and emit the harmonised table

10-minute grid, per-country `diary_days` flag carried through. ✅ **The day origin is DECIDED —
04:00, cyclic rotation, D-S2-5 — and this work item is no longer blocked on it.**

🔴 **The age floor moves from 11 to 10, and it is derived, not chosen.** The rule is *the harmonised
floor is the highest of the participating countries' minimum ages*, so that every country can supply
every age the corpus contains. **11 was France's minimum.** With France excluded (decision 16) the
participating minima are Spain **10**, the UK **8** and Italy **3**, so the binding floor is **10**.
Filter: **age ≥ 10**. *(Superseded: "Age ≥ 11".)* 🔴 **This is not a widened band** — it is the same
rule evaluated over a different country set, and it must be re-evaluated again if France ever returns,
in which case it goes back to 11.

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

🔴 **Rewritten 2026-08-15.** Step 1.3 must have emitted **all three** episode tables — Spain, the UK
and Italy — and they all exist. ✅ **D-S2-1 no longer blocks work item 2.4**; the origin is decided
(D-S2-5, 04:00, cyclic rotation).

**What still blocks this step: nothing external.** The one remaining precondition is the
**sixteen-gate Step 1 re-run** on the three countries (M-1..M-5 changed the record contract, so Step 2
must consume parquets written to the current contract, not the previous one). 🔴 **That is our own
work on our own cluster, not a queue in another institution** — which is the whole point of decision
16. *(Superseded: "Step 1.3 must have emitted all four episode tables… 2.4 waits on UK, France and
Italy.")*

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

### 2026-08-14 — four decisions taken after the Spanish file, D-S2-1 to D-S2-4

* Findings F-ES-1 to F-ES-4 in `../Step1_docs/outputs_step1/codebook_facts_spain.md` are resolved as
  D-S2-1 to D-S2-4 above. **Three of the four overturn a line this document had listed as decided,
  and all three of those lines came from `RL02` rather than from a file.** The pattern is the point:
  the first country measured broke the standard in three places out of the handful it could touch.
* 🔴 **The 04:00 origin is withdrawn rather than replaced.** Author call, 2026-08-14: the origin is
  decided from four measured codebooks or not at all. Setting it to 06:00 now would be the same
  error in the other direction — one country generalised to four. Work item 2.4 is blocked on it.
* **Co-presence keeps the five-flag core and adds country extras beside it.** `PADRES` survives as
  `cop_extra_es_padres`. The shared core is what carries the transfer claim; the extras are what
  stop a recorded field from being thrown away. Step 5 may not condition on an extra.
* **`RL02`'s location range rule is retracted and no range test replaces it.** Spain's `41` is public
  transport, above the range `RL02` gave, and present in the file. Ranges are how this class of
  defect stays silent; an explicit code-by-code crosswalk is how it cannot.
* The other three countries' origins, flags and location ranges are **measured, not assumed to match
  Spain either.** Spain is the first measurement, not the new standard.

### 2026-08-15 — 🔴 **STEP 2 IS UNBLOCKED. D-S2-1 closes as D-S2-5. The age floor moves 11 → 10.**

**Author decision 16 excluded France**, so the corpus is Spain, the UK and Italy — three countries, all
built, all with transcribed codebooks. Three things follow, and the first is the one that mattered.

* ✅ **D-S2-1 closes as D-S2-5: the day origin is 04:00, reached by treating each diary as a cyclic
  24-hour day.** D-S2-1's own condition was *"chosen from every measured codebook or not at all"*, and
  three is now every country. Measured: Spain **06:00**, Italy **04:00**, UK **04:00**. 🔴 **No
  re-basing is possible in either direction** — a 06:00 diary contains no 04:00-06:00 of its own
  calendar day — so the rotation takes those two hours from the tail of the same diary, and **that
  splice is written down rather than hidden in index arithmetic.** 04:00 wins because it splices **one**
  country instead of two, because the splice lands in the sleep block (which is exactly why the UK and
  Italy chose it natively, and it is HETUS's own guideline origin), and because two of three deliveries
  then need no transformation at all.
* 🔴 **Three consequences that are implementation work, not notes:** Spain's episode count *will* change
  (the episode straddling 04:00 splits), so the Step 2 count is a different quantity from Step 1's
  pinned 430,754 and must be reported as one; the rotation must be **invertible**, with a round-trip
  test back to the Step 1 table; and **`origin_hour` is metadata, never a serialised field** — a
  per-country origin column reaching Step 3 would leak country identity into LOCO by the front door
  after D-S2-2 closed the back one.
* **The age floor moves from 11 to 10, and it is derived, not chosen.** The rule is *the highest of the
  participating countries' minimum ages*. **11 was France's.** Without France the minima are Spain 10,
  UK 8, Italy 3, so the floor is **10**. 🔴 **Not a widened band** — the same rule over a different
  country set, and it returns to 11 if France is ever re-admitted.
* **`V2.a` moves 4 → 3** and **`G2.9` now compares three countries.** 🔴 **`G2.9`'s threshold was NOT
  touched, and note which way it moves:** three countries give **3 pairs instead of 6**, so there are
  half as many chances to clear 20 min/day on 3 of 10 categories. **The gate gets harder, not easier**,
  which is precisely why the numbers stay where they were pre-registered.

🔴 **What still blocks Step 2, and it is ours:** the **sixteen-gate Step 1 re-run**. M-1 to M-5 changed
the record contract (three-state `loc_raw`, nullable weights), so Step 2 must consume parquets written
to the current contract. **Step 2 does not start on stale parquets.**
