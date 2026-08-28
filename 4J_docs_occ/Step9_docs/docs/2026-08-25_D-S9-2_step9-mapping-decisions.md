# `D-S9-2` — the nine things Step 9 cannot decide for itself

#### 4J HETUS LLM pipeline, Step 9, item 9.1. Written 2026-08-25 (night).
#### Implementation: `../4thJ_09_enduseLoads.md`. Validation: `../4thJ_09_enduseLoads_val.md`.

---

## How to read this document

Every item below is a place where **the mapping could not be copied from a published source**, which
is exactly where `RL13`'s *"do not invent the mapping"* stops being advice and becomes a decision.

Each item states: what the source actually says, what was done **provisionally** so that the step
could be built and measured, **how much of the corpus it is worth**, and a recommendation.

🟢 **Nothing here blocks the build.** Items 1, 2, 5 and 6 are already implemented at the recommended
option and are held in **data files**, not code, so a ruling changes a CSV and a re-run, never a
tool. Items 3, 7, 8 and 9 change what a gate *reports*, not what the model does.

🔴 **Nothing here moves a registered threshold.** `G9.7` and `G9.11` are scored exactly as
`4thJ_09_enduseLoads_val.md` registers them, and both are expected to FAIL. Items 7 and 9 ask what
the manuscript should SAY about those failures, not whether to soften them.

---

## The artefacts these decisions govern

| file | what it is |
|---|---|
| `../outputs_step9/acl_to_crest_activity.csv` | the join key. **Items 1a/1b/1c edit this file and nothing else.** |
| `../outputs_step9/activity_appliance_map.csv` | 192 rows, generated from the join and the two source artefacts |
| `../outputs_step9/sources/crest_appliances_richardsonpy.csv` | CREST's 33 appliances, md5 `eba850becdc987b441f78244692f8ee2` |
| `../outputs_step9/sources/jordan_vajen_iea_task26_v2.0_2001.pdf` | the DHW report, md5 `c7c460924ef66588649b2473b706e2b9` |
| `tools/4thJ_step9_mapping.py`, `tools/4thJ_step9_trigger.py` | the builder and the trigger |

---

# Item 1 — the ACL-to-CREST join, where it is a judgement

**The situation.** CREST resolves activity at **six named states** — `0 watching TV`, `1 cooking`,
`2 doing laundry`, `3 washing`, `4 ironing`, `5 cleaning the house (vacuuming)` — plus three
non-activity handlers (`6 ACTIVE OCC`, `7 LEVEL`, `8 CUSTOM`). That list is not inferred: it is
printed in the docstring of the open re-implementation and vendored as
`sources/crest_activity_codes.txt`.

**Eight of the eleven joins are name-for-name correspondences between two published code lists** —
ACL `821` *Watching television* to `0 watching TV`, ACL `311` *Food preparation and preservation* to
`1 cooking`, and so on. Those are labelled `VALIDATED` and need no ruling.

**Three are not.** They are below, each with the share of modelled time it governs, measured on the
15,600 shipped Leg-5 diaries (22,464,000 modelled minutes).

### 1a — ACL `822` *Watching TV, film or video via PC or internet* → **0.0216 % of modelled time**

* **What the source says:** nothing. UK TUS 2000 has no such act, so CREST has no state for it.
* **The two readings:** it is *video playback* (profile `0`, which drives TV 1/2/3, VCR/DVD and the
  receiver box) or it is *computer use* (profile `6 ACTIVE OCC`, which drives the PC and printer).
* **Provisional:** profile `0`. The ACL level-2 group is `82` *television and video*, and the load
  being described is a display running video.
* **Worth:** 4,860 minutes of 22,464,000. **This item is worth two parts in ten thousand.**
* 🟢 **Recommendation (a): profile `0`.** Either answer is defensible and neither is measurable at
  this weight; keep the code with its own ACL group.

### 1b — ACL `312` *Dish washing* → **0.900 % of modelled time**

* 🔴 **This is the interesting one, and it is the one `G9.11` is about.**
* **What the source says:** CREST puts the **Dish washer** appliance on profile `1` (*cooking*),
  activity probability `0.1443`, alongside Hob, Oven, Microwave and Small cooking. It does that
  because UK TUS 2000 did not separate dishwashing from cooking. HETUS does — `312` is its own
  three-digit code.
* **The two readings:** (a) map `312` → profile `1`, which **reproduces CREST unchanged**; or (b)
  fire the dishwasher from `312` directly, which is more faithful to the diary and **is a
  three-digit resolution that is OURS**.
* **Provisional:** (a).
* 🔴 **Why (b) is not simply better.** Option (b) is precisely the move `RL13` forbids and `G9.11`
  was written to detect: a resolution no published model supports. It would also change the
  dishwasher's activity probability, and there is no published value for `P(dishwasher | dish
  washing)` to change it *to*.
* **Worth:** 202,100 minutes. Under (a) those minutes join cooking's eligible set and the dishwasher
  fires from a set roughly 44 % larger; under (b) the dishwasher fires from `312` alone and the hob,
  oven, microwave and small-cooking group lose those minutes.
* 🟢 **Recommendation (a): keep CREST's join.** And say so in the methods, because it is the
  clearest single illustration of the paper's own limitation: *the corpus resolves finer than any
  published consumer of it.*

### 1c — ACL `039` *Other personal care, specified or not* → **0.392 % of modelled time**

* **What the source says:** nothing. CREST's `3 washing` drives only the **Electric shower**, which
  is not in its default dwelling anyway.
* **The two readings:** `039` is the residual of ACL group `03`, which contains `031` *Washing and
  dressing*; either the residual travels with its group, or it is too heterogeneous to carry a
  hot-water draw.
* **Provisional:** profile `3`, residual travels with its group.
* 🔴 **This one matters more than its weight suggests**, because `031` and `039` are also two of the
  three ACL drivers of DHW category A (item 4). It is a DHW decision wearing an electricity
  decision's clothes.
* 🟢 **Recommendation (a): keep `039` with `031`.** The alternative silently narrows the DHW driver
  set, and a narrower driver set does not reduce the modelled volume — the calibration simply
  concentrates the same 200 l/day into fewer minutes, which is a **worse** answer, not a more
  cautious one.

---

# Item 2 — which of CREST's 33 appliances the dwelling owns

**The situation.** CREST's table carries two different ownership columns: `Has appliance? (1-yes,
0-no)`, its **default dwelling**, and `Dwellings with appliance`, a **stock share**.

**Provisional:** a dwelling owns an appliance if it is in CREST's default dwelling (`Has appliance?
= 1`, **23 of 33**) *and* a seeded draw falls under its `Dwellings with appliance` share — which is
CREST's own `randomize()` behaviour.

🟢 **Why this is not a judgement of ours.** The ten appliances CREST excludes from its default
dwelling are exactly the ten that would double-count:

| group | rows excluded | what already models it |
|---|---|---|
| **Electric Space Heating** | Storage heaters, Other electric space heating | **Step 8's EnergyPlus heating.** Including them would add a second space-heating load to a model that already has one |
| **Water heating** | DESWH, E-INST, Electric shower | **Item 9.3's Jordan & Vajen DHW model** |
| (stock variants) | Chest freezer, Upright freezer, Fax, TV 3, Washer dryer | second units and obsolete devices |

🔴 **So the non-double-counting exclusion is CREST's own default, not a choice we made to make the
numbers work.** That is worth stating plainly in the methods.

🔴 **What it costs, stated:** the `ownership_share` column is **UK 2000** ownership, applied
unchanged to Spain and Italy. The validation document already names this as a gap —
*"appliance stock ownership rates by country ... is a country-level input we do not have"* — and
this decision does not close it. It is limitation **E2**.

🟢 **Recommendation (a): keep CREST's default dwelling, keep the UK ownership shares, declare E2.**
The alternative — country-specific ownership — needs a data source we do not have, and inventing one
is item 1's problem again.

---

# Item 3 — 🔴 `G9.14`'s premise is FALSE, and the gate needs re-specifying

**`FINDING 137`.** The step document states, in bold:

> *"this step does not consume the real corpus. It consumes Step 7's generated diaries, and those
> carry no secondary activity at all, because `act2` is not serialised into the `DUR,ACT,LOC,COP`
> tuple."*

**That is not true.** Measured, not argued:

| evidence | what it shows |
|---|---|
| `tools/decoder.py:86-88` | the episode has **five** comma-fields, `dur, act, act2, loc, cop`, and raises if it does not |
| `Step7_docs/outputs_step7/step7_grammar.ebnf` line 2 | `# ACT 159 \| ACT2 43 \| LOC 5 \| COP 34` — the grammar declares 43 secondary codes |
| the shipped Leg-5 diaries, 15,600 records, 339,612 episodes, 0 undecodable | **29.816 % of episodes** and **26.308 % of modelled minutes** carry a non-empty `act2`, across **29 distinct codes** (es 32.113 % / 27.101 %, uk 26.933 % / 22.787 %, it 30.546 % / 29.034 %) |

🔴 **The consequence for the gate.** `G9.14`'s written rationale is *"a trigger rule reading `act2`,
a column the generated diaries do not carry, does not raise: the appliance simply never fires."*
**That failure mode does not exist.** A trigger reading `act2` from the generated record **would**
fire, on more than a quarter of modelled minutes.

🟢 **What is NOT affected.** `D-S9-1`'s ruling (d) stands. It rests on the precondition being
*unsatisfiable* — no fourth country after DECISION 16, and no slot basis outside Spain — not on
serialisation. The ruling is unchanged; one sentence supporting it is wrong.

**The options.**

* **(a)** Re-specify `G9.14` as a **policy assertion**: the trigger's runtime input columns must be a
  subset of the generated record's columns **and must not contain `act2`**, because `D-S9-1` ruled
  (d). The perturbation stays exactly as registered — add `act2` to the trigger's inputs — and the
  gate still falls on it, but now for the right reason.
* **(b)** Retire `G9.14` as based on a false premise.
* **(c)** Reopen `D-S9-1`: `act2` is available after all, so calibrate with it.

🟢 **Recommendation (a).** The gate is still worth having — it stops a silent policy breach — and
(a) is additive: it keeps the registered perturbation and tightens the reason. **(c) is rejected**:
the ruling's actual premise is untouched, and the paper's whole claim is that behaviour does not
transfer trivially, which is the one thing option (c) of `D-S9-1` would have contradicted.

🔴 **The step document's own sentence must be corrected forward**, with the measurement, exactly as
`FINDING 47` was.

---

# Item 4 — the DHW driver set is ours, and every DHW row says so

**The situation.** Jordan & Vajen's Table 1 gives four draw-off categories with flow rate, duration,
incidences per day, sigma and volume per load. It distributes those draw-offs **by a probability
function over year, weekday and day** — explicitly not by a time-use code.

**So which ACL codes fire which category has no published answer.** Provisional:

| category | ACL drivers | why |
|---|---|---|
| **A** short load (washing hands) | `031`, `039`, `312` | hand washing accompanies personal care and dish washing |
| **B** medium load (dish-washer) | `312`, `311` | the report's own parenthetical names the dishwasher |
| **C** bath | `031` | the only ACL code that names washing |
| **D** shower | `031` | as above |

🔴 **Every one of the seven DHW rows in the map is labelled `NOT VALIDATED`, and not because its
numbers are doubtful.** The numbers are Table 1's, transcribed. The **driver** is ours.

🟢 **Recommendation (a): keep the drivers, keep the `NOT VALIDATED` label, and state in the methods
that the DHW model's TIMING is ours while its VOLUME is Jordan & Vajen's.** That is the honest split
and it is the same shape as `D-S9-1`'s declared limitation: the rate survives, the timing does not.

---

# Item 5 — does the 200 l/day reference scale with household size?

**What the source says**, read from the report: *"a mean load volume of **200 litres per day** was
chosen for a **single family house**"*, with a basic profile of 100 l/day and higher demands built
*"in dual order (100, 200, 400, 800 liters ..)"* by **superposition**.

🔴 **The report gives no household size for its single family house, and no per-person figure at
all.** So a per-capita scaling cannot be read out of it.

**Provisional:** hold **200 l/day per dwelling, constant**, regardless of household size. This
invents nothing.

**What that produces**, measured on fold `es` (100 dwellings, 204 people):

| quantity | modelled | Table 1 |
|---|---:|---:|
| l per dwelling-day | **200.96** | 200 |
| category A events per dwelling-day | **27.999** | 28 |
| category B | **12.030** | 12 |
| category C | **0.1468** | 0.143 |
| category D | **2.0405** | 2 |
| l per **person**-day | **98.51** | *(not a quantity the report defines)* |

🔴 **Consequence: `G9.7` FAILS as registered.** Its band is 30–50 L/person/day and the model returns
98.51, because a 200 l/day dwelling with a mean of 2.04 people is 98 l/person/day by arithmetic.

**The options.**

* **(a)** Keep 200 l/day per dwelling. Report `G9.7` as a **FAIL** and explain that the registered
  band is a per-person quantity while the source's reference is per dwelling — see item 7.
* **(b)** Scale the daily volume linearly with household size against an assumed reference size
  (4 persons → 50 l/person/day, which lands inside the band). **This is reverse-engineering the
  model to pass a gate**, and the reference size would be ours.
* **(c)** Use J&V's superposition rule literally: 100 l/day per unit, one unit per *n* occupants.
  Needs the same missing *n*.

🟢 **Recommendation (a).** (b) is the move this project refuses — the band would be met by choosing
a divisor. The failure is informative and belongs in the results.

---

# Item 6 — how Table 1's `sigma = 2` is read

**The situation.** Table 1 gives `sigma = 2` for **all four** categories, and separately states
*"Flow rates in steps of **0.2 l/min** = 12 l/h are taken."* Category A's mean flow is **1 l/min**.

* Read as **2 l/min**: about **31 %** of category-A draws are negative. Clipping them to the
  smallest admissible flow biases the mean upward, and the model then returns **213.8 l/day** against
  the report's own 200 — it fails to reproduce Table 1's own arithmetic.
* Read as **2 steps = 0.4 l/min**: negative draws are 0.6 % of category A and negligible elsewhere,
  and the model returns **200.96 l/day**, reproducing every one of Table 1's derived quantities to
  better than 1 %.

**Provisional:** sigma is in units of the 0.2 l/min discretisation step.

🟢 **Recommendation (a): the step reading.** 🔴 It is a **reading**, not a transcription, and it is
recorded here rather than buried in the code comment because it is the only number in the DHW model
that is not read straight off the page. The test applied was the right one: *which reading
reproduces the source's own published totals?*

---

# Item 7 — 🔴 `G9.7`'s registered band is stated on a basis its source does not define

**`FINDING 138`.** Step 9's implementation document says the DHW model is *"roughly **30 to 50
L/person/day at 60 °C**"*, and the validation document registers `G9.7` as **30 to 50 L/person/day
at 60 °C, population median**.

`RL25` flagged that sentence as a collapse of two rows and offered a correction: *"a base of 50
L/person/day at 60 °C, with the 30-50 L figure belonging to the shower event at 40 °C."*

**The report was opened. Neither is what it says.**

| claim | what the report actually contains |
|---|---|
| our *"30–50 L/person/day at 60 °C"* | **not present.** No per-person volume, no 60 °C |
| `RL25`'s *"base 50 L/person/day at 60 °C"* | **not present.** The base is **200 l/day per single-family house** |
| `RL25`'s *"30–50 L shower event at 40 °C"* | **not present.** The shower is **8 l/min × 5 min = 40 l per load**, 2 loads/day |
| the reference temperature | the report's worked example uses a **35 K rise**, not a 60 °C set point |

🔴 So `RL25`'s correction was **right that our sentence was wrong** and **wrong about what the right
numbers are**. That is the third round in this project in which a vetting report's *diagnosis* was
sound and its *replacement values* were not — `FINDING 47` is the same shape.

**What is NOT proposed:** moving the band. It is registered and it stays.

**The options for what the manuscript says.**

* **(a)** Score `G9.7` as registered, report the **FAIL** (98.51 L/person/day in `es`), and publish
  a declared methodological limitation: the gate compares a per-dwelling reference against a
  per-person band at a reference temperature the source does not state — the same shape as
  `D-S8-5` item 1, where `G8.7` became a permanent `INFO` because it compared two structurally
  different models.
* **(b)** Make `G9.7` **INFO permanently**, as `D-S8-5` item 1 (a) did for `G8.7`, on the grounds
  that a band and a model that do not share a basis cannot be compared at all.
* **(c)** Re-register the band on the source's own basis (l per dwelling-day), which is a **band
  change** and would need to be declared as one.

🟢 **Recommendation (b), with the (a) reporting.** The precedent is exact: `G8.7` was made a
permanent `INFO` rather than scored, because the two sides of the comparison were not the same
quantity, and `FINDING 121` was published as a declared limitation instead. The same is true here.
🔴 **If the author prefers (a), the FAIL ships as a FAIL** — that is also fine and it is the more
conservative option.

> 🟢 **RULED 2026-08-27 — (d)(ii) → (b), TOGETHER WITH `D-S11-1`, AS THIS BLOCK ASKED.**
> The author's ruling is recorded in §8 of
> `../../Step11_docs/docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md` and what was executed against
> it in §9 of the same record. `G9.7` and `G11.7` are **permanent `INFO`** on the `G8.7` /
> `D-S8-5` item 1 (a) precedent; `FUENTES-2018` is in `citations.csv`; §9B names both papers and
> both bases; the manuscript reports the gap as a denominator incompatibility. 🔴 **The
> 30-50 band was NOT moved and `G9_7_BAND_L_PER_PERSON_DAY` is still `(30.0, 50.0)`** — the medians
> `100.16 / 117.65 / 91.06` are still computed and still printed as outside it. 🔴 **One
> thing the ruling did not foresee and that the execution surfaced: `G9.7` was the only detector of
> `scale_dhw_by_2`, so retiring it to `INFO` left that mutation caught by nothing. That is
> `D-S11-2`, and it is open.** Item 7 itself is closed.
>
> 🔴 **2026-08-27 — ITEM 7's EVIDENCE TABLE IS SUPERSEDED AND A FOURTH OPTION EXISTS. DO NOT RULE
> THIS ITEM FROM THE TABLE ABOVE.** Work item 11.2
> (`../../Step11_docs/docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`, findings `163`–`166`) found
> that the premise *"a basis its source does not define"* is wrong in a way that matters: **the band
> has a different source.** `RL13` row 15 attributes it jointly to Jordan & Vajen **and Fuentes et
> al. (2018)** (RSER 81(1): 1530–1547, DOI `10.1016/j.rser.2017.05.229`), and §9B of the parent
> document compressed the two into one. Fuentes is in **no citation table in this project**. The two
> rows of the table above reading *"`RL25`'s … not present"* are also **too broad**: all four of
> `RL25`'s event volumes match Table 1, and only its bases are absent.
>
> 🟢 **The new option (d) — cite the band's actual source and score it on its actual basis — is
> written up in `D-S11-1` §5, with the recommendation (d)(ii) → (b).** Ruling item 7 and ruling
> `D-S11-1` are the same decision and should be taken together. 🔴 **The band is not moved under any
> option**, and the sub-option that would meet it by *declaring an occupancy* is recorded there as
> refused.
>
> ⚪ **Item 5 is affected too and is NOT re-opened here.** Its ruling — hold 200 l/day constant,
> because a per-person scaling *"is not in the report and would be ours"* — is **correct as written**
> and is exactly why the scored quantity is `200 / n_members`. It would only reopen under option
> (d)(i), which is not recommended.

---

# Item 8 — `richardsonpy` is GPL-3.0 and its data file is vendored

**The situation.** `RL25` reported the CREST re-implementation's licence as *"Academic / MIT"*.
Checked against the GitHub API in a previous session, it is **GPL-3.0** — copyleft, not permissive.
That correction is already recorded.

**What was done:** `richardsonpy/inputs/Appliances.csv` and a 30-line excerpt of
`classes/appliance.py`'s docstring are vendored under `outputs_step9/sources/`, md5-stamped, with
their origin URL and licence recorded in `citations.csv`. **No `richardsonpy` code is imported or
copied into any tool**; `tools/4thJ_step9_trigger.py` re-implements CREST's state machine from the
published description.

🔴 **The distinction this project already recorded:** *"Adapting the published table from the paper
is a different act from copying the code, and only the second triggers the licence."* The vendored
CSV is a table of parameter values published in Richardson et al. (2010); the docstring excerpt is
30 lines of a code comment.

**The options.**

* **(a)** Keep both vendored, with the notice, and state the licence in the Data Availability
  section. Reproducibility requires the artefact to be on disk at a known md5.
* **(b)** Keep the CSV, drop the docstring excerpt and cite the activity-code list to the paper.
* **(c)** Vendor nothing and re-fetch at build time. **Rejected here**: a build that depends on a
  live URL is not reproducible, and `FINDING 47` is what happens when a citation cannot be
  re-checked against a fixed artefact.

🟢 **Recommendation (a).** 🔴 It is a licence question, not a technical one, and the author should
confirm it before the repository is released.

---

# Item 9 — `G9.11` will FAIL, and the premise is now confirmed from the artefact

**Already recommended twice** (2026-08-20, and again in the `D-S9-1` entry): *let it FAIL and report
it.* This item asks the author to close it formally, because the premise is now confirmed from a
**primary artefact** rather than from a research report.

`sources/crest_activity_codes.txt`, vendored from the re-implementation's own docstring:

```
0 - watching TV        3 - washing                 6 - ACTIVE OCC
1 - cooking            4 - ironing                 7 - LEVEL
2 - doing laundry      5 - cleaning the house      8 - CUSTOM
```

**Nine indices, six named activities, zero HETUS codes.** So a mapping adapted from CREST resolves
at six states and cannot possibly satisfy *"the number of distinct ACL codes with distinct appliance
rows must exceed the number of distinct 2-digit groups"*.

🟢 **Recommendation (a): record the FAIL, do not touch the band, and re-justify the three-digit
corpus decision on microdata fidelity** — the third digit exists in the source and discarding it to
flatter a gate is the move this project refuses. The gate was written to make this discoverable and
it worked.

🔴 One measurement to attach to that re-justification: **ACL `319` never occurs in the generated
corpus at all** (0 of 22,464,000 minutes), so five rows of the map are inert. Reported rather than
deleted, because a mapping row for a code the corpus does not contain is a different fact from a
missing row.

---

## Summary — what a ruling costs

| item | subject | recommended | changes | worth |
|---|---|---|---|---|
| 1a | ACL `822` join | (a) profile `0` | one CSV cell, re-run | 0.0216 % of time |
| 1b | ACL `312` join | (a) keep CREST's | one CSV cell, re-run | 0.900 % of time |
| 1c | ACL `039` join | (a) keep with `031` | one CSV cell, re-run | 0.392 % of time |
| 2 | ownership set | (a) CREST's default dwelling | nothing, declare E2 | the whole electricity total |
| 3 | `G9.14` premise | (a) re-specify as policy | the gate's reason, not its perturbation | the gate's validity |
| 4 | DHW drivers | (a) keep, `NOT VALIDATED` | nothing | DHW timing |
| 5 | 200 l/day scaling | (a) hold constant | nothing | `G9.7`'s verdict |
| 6 | Table 1 `sigma` | (a) 0.2 l/min steps | nothing | 6.9 % of DHW volume |
| 7 | `G9.7` basis | 🟢 **RULED 2026-08-27: (d)(ii) → (b)**, with `D-S11-1`, as asked. Permanent `INFO` on the `G8.7` precedent, band unmoved, citation repaired, gap reported as a denominator incompatibility. `D-S11-2` opened in its wake | what the gate reports, **plus one row in `citations.csv`** | a published FAIL |
| 8 | GPL-3.0 vendoring | (a) keep with notice | Data Availability text | release terms |
| 9 | `G9.11` | (a) FAIL and report | nothing | the corpus decision's justification |

🟢 **Every recommended option is already what is implemented and measured.** A ruling that accepts
all nine costs one line in this file and no re-run.

---

## Author's ruling

*(to be completed by the author)*
