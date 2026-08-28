# Step 9 — Activity-driven end-use loads

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 9. Validation: `4thJ_09_enduseLoads_val.md`

---

## STATUS

🟢 **ITEMS 9.1 TO 9.5 ARE BUILT, 2026-08-25 (night). The gate board is
16 PASS / 3 FAIL and the three FAILs are results, not defects.** 🔴 **CORRECTED 2026-08-26, `FINDING 149`: read `15 PASS / 3 FAIL / 1 NOT CHECKED`; the "16" counted `G9.4`'s NOT CHECKED as a PASS. Per-gate verdicts unchanged.** 100 dwellings per fold, the SAME
dwellings Step 8 simulated -- proven byte-for-byte against the shipped presence schedules, 100/100 in
every fold. No GPU, no Speed job, all local. Record: `docs/2026-08-25_items-9.1-9.5_the-mapping-the-trigger-and-the-campaign.md`.

🔴 **THREE FINDINGS REACH BACK OUT OF THIS STEP.** `FINDING 137`: this document's claim that
the generated diaries carry no `act2` is FALSE -- the tuple has five fields and **29.816 % of
episodes** carry one, so `G9.14`'s stated failure mode does not exist (see the addendum under
SECONDARY ACTIVITY below). `FINDING 138`: Jordan & Vajen's report was opened and contains **neither**
our "30 to 50 L/person/day at 60 C" **nor** `RL25`'s correction of it. `FINDING 141`: `D-S2-5`
harmonised the diary day onto a **04:00 origin**, and Step 7's emitter writes minute 0 into a
`Schedule:File` that EnergyPlus reads from midnight -- so **Step 8's 13,108 runs applied occupancy
four hours early**. Step 9 is corrected; Step 8 is the author's call, `D-S9-3`.

⚪ Two decisions are open and both are the author's: **`D-S9-2`** (nine items, all nine already
implemented at the recommended option) and **`D-S9-3`** (`FINDING 141`, recommendation (a)).

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

> 🔴 **SUPERSEDED 2026-08-20 — `FINDING 47`: THIS NOTE IS ITSELF A CONFLATION.** `41(7):780-788` names
> no real paper. `41(7):781-789` is **Richardson** et al., *Domestic lighting*; the real Widén lighting
> paper is **41(10):1001-1012**; and the Widén 2009 paper Step 9 actually needs is **41(7):753-768**,
> *Constructing load profiles for household electricity and hot water from time-use data*. The DOI
> `RL17` "CrossRef-verified" for it resolves to a paper on **passive cooling in Brazil**. See the
> `2026-08-20` progress-log entry for the four corrected references.

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

> 🔴 **SUPERSEDED IN PART, 2026-08-25 -- `FINDING 137`: THE SENTENCE ABOVE IS FALSE.**
> The generated diaries **do** carry `act2`. `tools/decoder.py:86-88` asserts the episode has
> **five** comma-fields, `dur, act, act2, loc, cop`; the Step 7 grammar declares **43** `ACT2` codes;
> and measured on the 15,600 shipped Leg-5 diaries (339,612 episodes, 0 undecodable),
> **29.816 % of episodes and 26.308 % of modelled minutes carry a non-empty `act2`**, over 29
> distinct codes (es 32.113 / 27.101 %, uk 26.933 / 22.787 %, it 30.546 / 29.034 %).
>
> 🟢 **`D-S9-1`'s ruling (d) is untouched** -- it rests on the precondition being
> unsatisfiable, not on serialisation. 🔴 **But `G9.14`'s rationale is void**: a trigger
> reading `act2` would fire, on more than a quarter of modelled minutes. The gate is re-specified as
> a POLICY assertion in `D-S9-2` item 3, and its registered perturbation is unchanged.

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
  with four measured rates, no calibration uses `act2` at all — Step 3's rule that no step conditions 🔴 *(see `D-S9-1`, 2026-08-20: "four" is stale and the slot basis is Spain-only.)*
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

🔴 *(2026-08-20: "all four countries" is pre-decision-16. There are **three**. See `D-S9-1`.)*

**If all four countries turn out to record `act2` at a usable rate**, Step 3 may serialise it, and
this step is the reason to. 🔴 **That decision has to be taken before the corpus is emitted**, because
adding a fifth tuple element afterwards invalidates the corpus, the grammar and every trained fold.

---

## DOMESTIC HOT WATER

The load that matters most in a well-insulated dwelling, and **3J found the DHW plant load-bearing in
its energy result.**

* **Jordan and Vajen four-event tapping model**: short draw, medium draw, bath, shower.
* Roughly **30 to 50 L/person/day at 60 °C**. 🔴 **DO NOT QUOTE THIS LINE. SUPERSEDED
  2026-08-25, `FINDING 138`: the report was opened and it contains no per-person volume and no
  60 °C anywhere.** Table 1's reference is **200 l/day for a single family house** at a **35 K**
  rise, made of A 1 l/min x 1 min x 28/day = 28 l, B 6 x 1 x 12 = 72 l, C 14 x 10 x 0.143 = 20 l,
  D 8 x 5 x 2 = 80 l. `RL25`'s correction ("base 50 L/person/day at 60 °C, 30-50 L for the shower
  at 40 °C") is **also** absent from the report. 🔴 `G9.7`'s registered band is therefore
  stated on a basis its own source does not define, and **the band was NOT moved**: it is scored as
  registered, it FAILS, and `D-S9-2` item 7 asks what the manuscript should say about that.
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

🟢 **NOTHING BLOCKS THIS STEP ANY MORE, 2026-08-25: both inputs existed and items 9.1 to 9.5
are built.** 🔴 **What is now blocked on the author is `D-S9-3`** -- `FINDING 141`, the
04:00 diary origin -- because Step 9's profiles cannot ship beside Step 8's occupancy schedules until
the two agree about what time it is inside the same building.

---

## DEFINITION OF DONE

1. Mapping table complete, every row cited to a published model and table.
   🟢 **DONE** -- 192 rows, `G9.1` PASS over 61 load-bearing rows.
2. Every row labelled VALIDATED or NOT VALIDATED with its validation scale.
   🟢 **DONE** -- `G9.2` PASS over all 192, keyed on the structured field (`V9.e`).
3. Two-stage trigger implemented with cycle-to-completion behaviour.
   🟢 **DONE** -- `G9.5` PASS, and seen failing on the registered truncation perturbation.
4. DHW implemented with an **assignment** check as well as a value check.
   🟢 **DONE** -- `G9.9` PASS over 300 `WaterUse:Equipment` objects re-read from the SAVED
   IDF, and seen failing on a re-pointed object whose values never moved.
5. Results reported at stock scale only.
   🟢 **DONE** -- item 9.5 refuses to write an aggregate over fewer than 100 dwellings, and
   `G9.13` PASS with `V9.d`'s coverage clause.
6. All Step 9 gates PASS and each has been seen failing.
   🔴 **NOT MET, AND NOT MET BY DESIGN.** The board is **15 PASS / 3 FAIL / 1 NOT CHECKED** (🔴 written here on 2026-08-25 as "16 PASS / 3 FAIL"; corrected 2026-08-26, `FINDING 149`): `G9.6`
   (`FINDING 139`, saturation), `G9.7` (`FINDING 138`, the band's basis) and `G9.12` (R2 0.26-0.31
   against 0.85). All three ship FAIL and **no band was relaxed**. 🔴 Their three registered
   perturbations therefore demonstrate nothing about them and are reported as
   `ALREADY_FAILING_AT_BASELINE` -- the vacuity condition, the same shape Step 6 recorded for its
   Leg-5 coverage clause.

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

> 🔴 **SUPERSEDED 2026-08-20 — THIS PRECONDITION CAN NEVER BE SATISFIED.** There is no fourth country
> (decision 16), and the **slot basis does not exist for the UK or Italy at all** — both ship episodes
> natively. See the `2026-08-20` progress-log entry and **`D-S9-1`**. Note that the status quo is not
> "blocked pending a measurement"; it is option **(d)** — `act2` unused — in force by default.

### 2026-08-20 — 🔴 **THE `act2` PRECONDITION THIS STEP SET ITSELF CAN NEVER BE SATISFIED. `D-S9-1` FOR THE AUTHOR.**

Found by reading, not by running. Nothing in Step 9 has been built, so nothing failed — but the
precondition is a **gate on a gate**, and one that can never open is indistinguishable, in its own
output, from one that is simply still waiting.

**The clause, unchanged above, the last sentence of the third entry:**

> *"no calibration uses it at all until `../Step3_docs/outputs_step3/act2_coverage.md` carries four
> measured rates — now required on **both** bases."*

**`act2_coverage.md` exists and is complete.** It cannot ever carry four rates on both bases, for two
independent reasons, and only the first is a bookkeeping error.

#### Reason 1 — there is no fourth country. Bookkeeping.

Author decision 16 (2026-08-15) excluded France. The corpus is **ES, UK, IT**. `act2_coverage.md`'s
own title is *"three countries, two bases, never mixed"*. **"Four" is a survivor of the pre-decision-16
design**, in the same class as `V6.d`'s four-fold assertion corrected in
`../Step6_docs/4thJ_06_transfer_val.md` on the same day. Read as **three**, it is satisfiable.

#### 🔴 Reason 2 — the slot basis does not exist for two of the three countries, and never will.

This one is **not** a bookkeeping error and does not go away by changing a number. The third entry
above pins this calibration to **slots, not episodes**, on a correct argument: the episode column is a
lossy first-of-run summary of the very stream the calibration is trying to recover. But
`act2_coverage.md` §2 measures a slot share for **Spain only**, and states why:

> *"The UK and Italy ship episodes natively and have no slot base at all."*

Confirmed there from Step 1's own reader documentation — the UK reader *"reconstructs nothing"* and
Italy's diary arrives with explicit `oraini`/`minini`/`orafin`/`minfin`, *"no slot reconstruction"*.
Spain's slot share exists **because Spain's episodes are reconstructed from 10-minute slots**; the
other two have no slots to count. `act2_coverage.md` §4 makes the same structural point for the
mixing counts, and is careful that these are **inapplicable by construction, not zero**.

**So "both bases, all countries" is not a measurement anyone has failed to take. It is a quantity
that does not exist**, and no amount of Step 3 work produces it.

#### What this actually costs, stated rather than assumed

The rates that **do** exist, from `act2_coverage.md`'s own summary table:

| Country | episode share (`act2` mapped, post-filter) | slot share |
|---|---:|---:|
| ES | 18.02 % | **12.24 %** |
| UK | 27.98 % | **no slot base** |
| IT | 23.99 % | **no slot base** |

🔴 **On the one country where both exist, they differ by roughly `1.5×`** (18.02 % vs 12.24 %) — and
`act2_coverage.md` warns explicitly that the two *"differ by a factor that depends on episode length,
i.e. instrument design, not respondent behaviour."* That is exactly why the third entry chose slots.
**Calibrating ES on slots and UK/IT on episodes would put a country-dependent instrument artefact
straight into `P(appliance | activity)`** — the same class of defect as the country-dependent MAPE
rounding floor recorded as `FINDING 39` in Step 6, and it would land invisibly, since a trigger
probability has no units that would look wrong.

#### `D-S9-1` — four options, none of which this step may take on its own

| | ruling | what it costs |
|---|---|---|
| **(a)** | Calibrate `act2` on the **episode** basis for all three countries, uniformly. | Abandons the third entry's slot argument. The Spain number becomes `18.02 %`, a **lossy** rate — but lossy *identically* for all three, so no country-dependent artefact. **Recommended** if `act2` is used at all. |
| **(b)** | Calibrate on slots where they exist, episodes elsewhere. | 🔴 **Rejected here as written** — it is the country-dependent artefact above, and it is invisible downstream. |
| **(c)** | Calibrate `act2` on **Spain only** and apply the Spanish trigger probabilities to all three. | Honest about the basis, but silently assumes secondary-activity behaviour transfers across countries — in a paper whose entire claim is that behaviour does **not** transfer trivially. |
| **(d)** | **Drop `act2` from the calibration entirely.** | The trigger fires from the primary code alone — which is what CREST, Widén, LPG and RAMP all do. Costs the *rate* absorption the third entry wanted; costs **nothing** the step ever had, since `act2` was never a runtime field. Cleanest, and already the documented fallback. |

**Nothing above touches `G9.14`**, which asserts `act2` is absent from the *generated* record. That
gate is correct under every option, including (d), and its perturbation is unaffected.

🔴 **Until `D-S9-1` is ruled, this step's own rule stands and no calibration uses `act2` at all** —
which, note, is operationally identical to option (d). **The current state is not "blocked pending a
measurement"; it is option (d) in force by default, undeclared.** That is the part worth ruling
deliberately rather than inheriting.

### 2026-08-20 — 🔴 **`FINDING 47`. THE CITATION CORRECTION THAT DEFINES `G9.4` IS ITSELF A CONFLATION, ON THREE COUNTS, AND THE DOI IT RESTS ON RESOLVES TO A PAPER ABOUT PASSIVE COOLING IN BRAZIL.**

`RL25` came back and was vetted. It did not flag this; it simply reported the correct bibliographic
data, and the error surfaced when that data was compared against our own note. **Every claim below was
re-derived from the CrossRef API in this session, not taken from the report.**

#### What this document says, above, in the "Citation note, from the vetting record"

> *"`RL08` gave Widén and Wäckelgård (2010) as Applied Energy 87(3):780-789. That is a conflation with
> Widén et al. 2009, Energy and Buildings **41(7):780-788**."*

`../Step9_docs/4thJ_09_enduseLoads_val.md`'s `G9.4` row repeats it, and names it as **the example the
gate exists to catch**: *"41(7):780-788 is the different 2009 lighting paper"*.

#### What CrossRef actually returns

| DOI | resolves to | journal, vol(iss):pages |
|---|---|---|
| `10.1016/j.apenergy.2009.11.006` | *A high-resolution stochastic model of domestic activity patterns and electricity demand* — **Widén & Wäckelgård** | *Applied Energy* **87(6):1880-1892** |
| `10.1016/j.enbuild.2009.02.013` | *Constructing load profiles for household electricity and hot water from time-use data* — **Widén**, Lundh, Vassileva, Dahlquist | *Energy and Buildings* **41(7):753-768** |
| `10.1016/j.enbuild.2009.02.010` | *Domestic lighting: A high-resolution energy demand model* — 🔴 **RICHARDSON**, Thomson, Infield, Delahunty | *Energy and Buildings* **41(7):781-789** |
| `10.1016/j.enbuild.2009.05.002` | *A combined Markov-chain and bottom-up approach to modelling of domestic lighting demand* — **Widén**, Nilsson, Wäckelgård | *Energy and Buildings* 🔴 **41(10):1001-1012** |
| 🔴 `10.1016/j.enbuild.2009.02.006` | 🔴 *Estimation of passive cooling efficiency for environmental design in Brazil* — Oliveira, Hagishima, Tanimoto | *Energy and Buildings* **41(8):809-813** |

#### The three errors, separately, because they have different causes

1. 🔴 **Wrong author.** `41(7):781-789` is **Richardson et al.**, not Widén. Our note attributes a
   Richardson paper to Widén — the *same* class of error the note was written to fix, one issue over.
2. 🔴 **Wrong issue and wrong pages for the real Widén lighting paper.** It exists, but it is
   **41(10):1001-1012**, not 41(7):780-788. The page range `780-788` in our note belongs to **no paper
   in this set**; it is one off from Richardson's `781-789`.
3. 🔴 **The DOI the correction was "verified" against is fabricated.** `RL17`'s `B9` row tabled
   `10.1016/j.enbuild.2009.02.006` as *"Fact / CrossRef API and Elsevier ScienceDirect / Tier 1 / H"*
   for the Widén lighting paper. **It resolves to a paper about passive cooling in Brazil.** A DOI
   presented as CrossRef-verified, that CrossRef contradicts, is the strongest possible signal in the
   vetting record and it sat unexamined for six days.

#### The corrected entries — use these, and nothing above them

* **Widén, J. & Wäckelgård, E. (2010).** *A high-resolution stochastic model of domestic activity
  patterns and electricity demand.* **Applied Energy 87(6): 1880-1892.**
  `10.1016/j.apenergy.2009.11.006`
* **Widén, J., Lundh, M., Vassileva, I. & Dahlquist, E. (2009).** *Constructing load profiles for
  household electricity and hot water from time-use data.* **Energy and Buildings 41(7): 753-768.**
  `10.1016/j.enbuild.2009.02.013` — 🔴 **this is the Widén paper Step 9 actually needs**, because it is
  the one that builds loads *and hot water* from time use.
* **Widén, J., Nilsson, A. M. & Wäckelgård, E. (2009).** *A combined Markov-chain and bottom-up
  approach to modelling of domestic lighting demand.* **Energy and Buildings 41(10): 1001-1012.**
  `10.1016/j.enbuild.2009.05.002`
* **Richardson, I., Thomson, M., Infield, D. & Delahunty, A. (2009).** *Domestic lighting: A
  high-resolution energy demand model.* **Energy and Buildings 41(7): 781-789.**
  `10.1016/j.enbuild.2009.02.010`

**Four distinct real papers, three authors' names in play, two of them in the same issue.** Cite each
for its own contribution. `G9.4`'s example text must be rewritten against this table.

#### 🔴 What this changes about `G9.4` itself, and it is not just the example

`G9.4` reads *"every cited DOI resolves to the title it is cited under."* **That test would have
PASSED our own note**, because the note carried no DOI — only a journal, volume, issue and page range.
`RL17`'s fabricated DOI would have failed it, but `RL17` is a research report, not a citation in our
bibliography.

**So `G9.4` as written cannot see the error it was created to describe.** It must additionally require
that **volume, issue, page range and first author** match what CrossRef returns for the DOI, not only
the title. Recorded as an amendment to make before `activity_appliance_map.csv` is built, not after.

#### Where else the wrong claim propagated, all corrected forward on 2026-08-20

* `4thJ_09_enduseLoads.md` — the citation note above.
* `4thJ_09_enduseLoads_val.md` — the `G9.4` row.
* `../DeepResearchPrompts/L25_activity_to_appliance_mapping.md` Part C — which passed the wrong claim
  **into the prompt**, though it did instruct the assistant to *"verify both independently and say so
  if our own correction is wrong"*. 🟢 **That instruction is the reason this was caught**, and it is
  worth keeping in every future prompt.
* `../DeepResearchPrompts/README.md` — the Wave 9 note.
* `../4thJ_00_HETUS_LLM_Pipeline.md` lines 102-103 carry only the *Applied Energy* half, which is
  **correct** and needs no change.

### 2026-08-20 — 🟡 **`RL25` VETTED. THE STRONGEST ROUND THIS SERIES HAS HAD ON CITATIONS, AND IT KILLS `G9.11`'s PREMISE: ZERO OF THE FOUR MODELS RESOLVE AT THREE DIGITS, OR EVEN TWO.**

Vetted by re-deriving, not by reading. Every bibliographic claim was re-queried against CrossRef in
this session and **all eight DOIs resolved to the exact title, volume, issue, page range and first
author `RL25` gave.** That is unprecedented in this series and it is the reason `FINDING 47` above
exists at all: the report's data was right, and comparing it with our own note is what exposed ours.

#### 🔴 The finding that changes a corpus decision's justification: `G9.11` cannot pass

`G9.11` requires the mapping to **actually use** the third digit — *"the number of distinct ACL codes
with distinct appliance rows must exceed the number of distinct 2-digit groups"*, with the note that
*"a mapping that resolves only at 2-digit did not need the corpus decision that preserved 3-digit
codes, and that should be known"*.

**Now it is known.** `RL25` reports the resolution of each source model:

| model | activity states it resolves | keys on |
|---|---|---|
| CREST (Richardson 2010) | **6** activity profiles + active occupancy | UK 2000 TUS |
| Widén et al. | **9-10** discrete states | Swedish SCB 1996 TUS |
| LoadProfileGenerator | 500+ bespoke *Affordances*, **0 TUS codes** | German bespoke ontology |
| RAMP | **0** — no activity mapping at all | user-defined time-of-use windows |

🔴 **Zero of the four use HETUS. Zero resolve at three digits. Two do not resolve on TUS codes at all.**

**What this does and does not mean.** It does **not** mean the corpus decision was wrong: three-digit
codes cost nothing to keep and the corpus is richer for them. It **does** mean the stated
justification — *"this step is why the `ACT` field kept three digits"* — **cannot be supported by the
downstream mapping**, because no published mapping consumes that depth. Any three-digit resolution in
`activity_appliance_map.csv` would be **ours**, which is precisely what *"do not invent the mapping"*
forbids. **`G9.11` as written will FAIL, and it should be allowed to fail rather than be reworded.**
It was written to make this discoverable and it worked.

#### What else `RL25` settles

* **Only 2 of 4 publish an actual mapping table**: CREST (Richardson 2010, Table 1, 33 appliances) and
  Widén (2009 Tables 1-2; 2010 Table 1). LPG's mapping lives inside `profilegenerator.db3`; **RAMP has
  none** — a clean `NOT FOUND` where one was possible.
* **`B2`'s single-stream question came back as we expected: 0 of 4 use concurrent secondary streams.**
  🔴 **Low diagnostic value — the prompt told them we believed this**, so the confirmation is worth
  less than it looks. `RL25` nevertheless claims *"exactly 0 convenient findings"*; **that count is
  wrong by at least one**, and it is the one place the report flatters itself.
* 🔴 **A correction to OUR document, which is what a good round does.** This step says the DHW model is
  *"roughly 30 to 50 L/person/day at 60 °C"*. `RL25` reports Jordan & Vajen as a base of **50
  L/person/day at 60 °C**, with the 30-50 L figure belonging to the **shower event at 40 °C** — a
  different quantity at a different reference temperature. **Our range appears to be two numbers from
  different rows collapsed into one.** Not yet verified against the IEA Task 26 report itself, which is
  the next check, but the sentence in this document should not be quoted until it is.
* **Licences, verified here against the GitHub API rather than taken from the report:**

| repo | `RL25` says | actually | verdict |
|---|---|---|---|
| `RAMP-project/RAMP` | EUPL-1.2 | **EUPL-1.2** | ✅ |
| `FZJ-IEK3-VSA/LoadProfileGenerator` | MIT | **MIT** | ✅ |
| `RWTH-EBC/richardsonpy` (CREST) | *"Academic / MIT in richardsonpy"* | 🔴 **GPL-3.0** | ❌ **WRONG** |

🔴 **`richardsonpy` is GPL-3.0, not MIT, and the difference is copyleft versus permissive.** If CREST
logic is vendored from that repository believing it MIT, the obligation is misjudged. **Adapting the
*published table* from the paper is a different act from copying the code**, and only the second
triggers the licence. Recorded before anything is vendored.

#### The one part of `RL25` that is not evidence

`B14` — *"naive occupant-level mapping duplicates shared appliances, inflating coincident peak by
**30 % to 75 %**"* — is marked `Inference`, source *"Behavioral load aggregation dynamics in shared
housing archetypes"*, which is not a document. **The mechanism is real and worth acting on** (one
dwelling should not run two dishwashers because two occupants both cooked); **the range is unsourced
and must not be quoted.** Same shape as `RL24`'s `B19`. Also unsourced: `B9`'s media-load figures
(*"25-45 % of viewing time, ~50-120 kWh/year, 1.5-3.5 % of electricity"*), attributed to three authors
without a table.

`B1`'s *"Table 1 listing 33 appliances"* and `B12`'s *"CV(RMSE) > 80 % at single-dwelling scale"* were
**not** verified here — the papers are paywalled and reconstructing a paywalled table is forbidden.
Recorded as **UNVERIFIED**, not as accepted.

#### What Step 9 owes next, in order

1. 🔴 **Ruling on `D-S9-1`** (the `act2` basis) — still open, still blocking, and `RL25` does not touch
   it.
2. **Decide what `G9.11` failing means.** Recommendation: **let it FAIL and report it**, and re-word
   this step's "why the `ACT` field kept three digits" section so the corpus decision is justified by
   corpus fidelity rather than by a downstream consumer that does not exist.
3. **Open the Jordan & Vajen IEA Task 26 report** and settle the 30-50 versus 50 L/person/day question
   at its stated reference temperature before either number enters a document.
4. **Amend `G9.4`** per `FINDING 47`: title-matching is not enough; volume, issue, pages and first
   author must all match CrossRef.

---

### 2026-08-20 (evening) — 🟢 **`D-S9-1` RULED (d): `act2` IS DROPPED FROM THE CALIBRATION. THE UNSATISFIABLE PRECONDITION IS DISSOLVED, AND THE STEP'S UNDECLARED DEFAULT BECOMES A DECLARED DECISION.**

**Ruled by the author 2026-08-20.** The appliance trigger fires from the **primary activity code
alone**.

#### What the ruling actually changes, which is less than it looks and matters more

🔴 **Option (d) was already in force — undeclared.** This step's own rule was *"no calibration uses
`act2` until `act2_coverage.md` carries four measured rates, on both bases"*, and that precondition can
**never** be satisfied: there is no fourth country after DECISION 16, and **the slot basis does not
exist for the UK or Italy at all** — they ship episodes natively, and only Spain reconstructs episodes
from slots. So the step has been operating as (d) by default since the precondition was written.
**The ruling does not change behaviour; it changes the behaviour from an accident into a decision**,
which is the only version that can be defended in a paper.

**The unsatisfiable precondition is now retired.** It is not "still blocking", it is **superseded**.
`act2_coverage.md` is no longer owed.

#### 🟢 The ruling is corroborated by the external literature, independently of our own reasoning

`RL25` established, per model and from the sources: **zero of CREST, Widén, LoadProfileGenerator and
RAMP drive from more than one concurrent activity stream.** All four use a single primary stream. So
adopting them unchanged is **the conservative choice, not a compromise** — which is what B2 was written
to find out, and it came back the way we expected.

🔴 **B2's diagnostic value is limited and this must be said with the result**: our prompt told the
report what we believed, so the confirmation is worth less than a blind finding would have been. The
ruling does not rest on it alone; it rests on the precondition being unsatisfiable.

**Rejected:** (a) episode-basis-for-all was the right answer *if `act2` were used at all*, and it is
not; (b) was already rejected as a country-dependent artefact invisible downstream; (c) assumes
secondary-activity behaviour transfers across countries, in a paper whose entire claim is that
behaviour does **not** transfer trivially — the one option that would have contradicted the thesis in
its own machinery.

#### What is untouched

**`G9.14` is correct under this ruling**, as it was under every other: it asserts `act2` is absent from
the **generated** record, which remains true, and its perturbation is unaffected.

🔴 **The limitation does not disappear with the field.** A load that is only ever recorded as a
*secondary* activity — a television on while eating, a washing machine running while the respondent
does something else — is **invisible to a primary-only stream**. That is now a **declared limitation of
the method**, in the same class as CREST's and Widén's, rather than a gap we intended to close. `RL25`
found **no published measurement** of how much energy such loads represent, so the limitation is
bounded by nothing and must be stated as unbounded.

#### The interaction with today's Step 7 ruling, which is small and worth being explicit about

`D-S7-1(c)` was ruled the same day: `000` is carried as its own state. `000` has a duration but **no
activity**, so under (d) it has **no appliance trigger** — there is no secondary code left to rescue it
from. Measured today from the corpus: `000` is **`0.1417 %` of modelled time** (not the `0.43 %` of
*episodes* this document has been quoting), ranging `es 0.304 %` to `it 0.018 %`, a **17x** per-fold
spread. **Report it per fold on the time basis.**

#### 🔴 Still open in Step 9, in order — the ruling closes one item and not the others

1. 🟢 **`D-S9-1` — CLOSED (d).**
2. **`G9.11` — still open, and my recommendation is unchanged: let it FAIL and report it.** `RL25`
   settled the premise by measurement: **zero of the four models resolve at three digits, or even at
   two** — CREST **6** activity profiles, Widén **9-10** states, LPG **0** TUS codes (bespoke
   ontology), RAMP **0** (no activity mapping at all). So the stated justification, *"this step is why
   the `ACT` field kept three digits"*, **cannot be supported by the downstream mapping**, because no
   published mapping consumes that depth. 🔴 **The corpus decision itself was not wrong** — three-digit
   codes cost nothing and the corpus is richer for them — **but it must be re-justified on corpus
   fidelity, not on a consumer that does not exist.** Any three-digit resolution we invented in
   `activity_appliance_map.csv` would be **ours**, which is precisely what *"do not invent the
   mapping"* forbids. The gate was written to make this discoverable and it worked.
3. **Jordan & Vajen, IEA Task 26 — still owed.** This document says DHW is *"roughly 30 to 50
   L/person/day at 60 °C"*. `RL25` reports the base as **50 L/person/day at 60 °C**, with **30-50 L
   belonging to the shower event at 40 °C** — a different quantity at a different reference
   temperature. 🔴 **Our range looks like two numbers from different rows collapsed into one. Do not
   quote the sentence in this document until the report itself is opened.**
4. **`G9.4` — still owed, per `FINDING 47`.** Title-matching is not enough: the gate must match
   **volume, issue, pages and first author** against CrossRef. As written it **would have passed our
   own wrong note**, because that note carried no DOI.

**`prereg.md` not touched**, md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified against its sidecar while
this entry was written.

### 2026-08-25 (night) — 🟢 **ITEMS 9.1 TO 9.5 ARE BUILT. NOTHING IN THE MAPPING WAS INVENTED, AND SIX FINDINGS CAME OUT OF BUILDING IT — THREE OF THEM REACHING BACK INTO STEPS 2, 7 AND 8.**

Record: `docs/2026-08-25_items-9.1-9.5_the-mapping-the-trigger-and-the-campaign.md`.
Decisions raised: `docs/2026-08-25_D-S9-2_step9-mapping-decisions.md` (nine items),
`docs/2026-08-25_D-S9-3_FINDING-141_the-diary-day-starts-at-0400.md`.

**All local. No GPU, no Speed job, nothing on the cluster.**

🟢 **The mapping is sourced, not invented.** Four primary artefacts were retrieved and
vendored under `outputs_step9/sources/` with their md5s: CREST's appliance table as distributed in
`richardsonpy/inputs/Appliances.csv` (`eba850be…`), its activity-profile code list, its 10-minute
activity statistics, and Jordan & Vajen's IEA-SHC Task 26 report (`c7c46092…`). `RL25`'s `B1`
claim — which `RL25` itself could only report as UNVERIFIED, the paper being paywalled — is now
**verified**: the artefact carries **exactly 33 appliance rows**. LoadProfileGenerator and RAMP were
examined and supply nothing, exactly as `RL25` said.

`activity_appliance_map.csv`: **192 rows, 141 ACL codes, 43 VALIDATED / 149 NOT VALIDATED**, 54
electricity rows, 7 DHW rows and **131 explicit no-load rows that claim nothing**. 🔴 The one
thing in it that is ours is the ACL-to-CREST join, and it lives in `acl_to_crest_activity.csv` so a
ruling edits data and never a tool.

🔴 **`FINDING 137` — THIS DOCUMENT WAS WRONG ABOUT `act2`.** The generated diaries DO carry
it: the episode tuple has **five** comma-fields (`tools/decoder.py:86-88`), the grammar declares 43
`ACT2` codes, and **29.816 % of episodes / 26.308 % of modelled minutes** carry one across the
15,600 shipped Leg-5 diaries. `D-S9-1`'s ruling (d) stands — it rests on the precondition being
unsatisfiable — but **`G9.14`'s stated failure mode cannot happen** and the gate is re-specified as
a policy assertion.

🔴 **`FINDING 138` — THE DHW RANGE IS ABSENT FROM ITS SOURCE, AND SO IS `RL25`'s CORRECTION
OF IT.** The report was opened, as this step owed itself. Table 1's reference is **200 l/day for a
single family house** at a **35 K** rise; there is no per-person figure and no 60 °C anywhere.
`G9.7`'s band was **not moved** and it FAILS.

> 🔴 **CORRECTED 2026-08-27 by work item 11.2** —
> `../Step11_docs/docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`, findings `163`–`166`.
> **Nothing above is withdrawn and no Step 9 number changes**: the report really does contain no
> per-person volume and no 60 °C, `G9.7` still **FAILS 300**, and the band is still unmoved. Two
> things are added.
>
> **(1) The band was never Jordan & Vajen's, so its absence from that report was never evidence
> about the band.** It enters this project at `DeepResearchPrompts/RL13_…` row 15 (2026-08-14,
> Tier 2), which attributes *"30 to 50 L/person/day at 60 deg C"* jointly to Jordan & Vajen **and to
> Fuentes et al. (2018)**, *A review of domestic hot water consumption profiles…*, RSER 81(1):
> 1530–1547, DOI `10.1016/j.rser.2017.05.229`. §9B of the parent document compressed that row to one
> attribution. **Fuentes is in no citation table in this project, `outputs_step9/citations.csv`
> included.** `FINDING 138` opened the right report and asked the wrong one — the general lesson
> being that a value's **source** is a claim needing its own check, separate from the value.
>
> **(2) `RL25`'s VOLUMES were sound; only its BASES were not.** Short 1–2 L against Table 1's 1;
> medium 6 L against 6, exact; bath 100–140 L against 140; shower 30–50 L against 40 — **4 of 4
> consistent**. The per-category temperatures and the 50 L/person/day base are **absent**, exactly as
> stated above. The sentence *"and so is `RL25`'s correction of it"* is therefore **too broad** and
> should be read as applying to the bases alone.
>
> ⚪ Also established, and it is the operative part: `G9.7`'s scored quantity reduces to
> **`200 / n_members`** to within 0.0005 over all 300 rows, so the gate measures household size.
> **`D-S11-1`** carries the question forward; `D-S9-2` item 7's option set is extended there, not
> here.

🔴 **`FINDING 139` — THE CORPUS DOES NOT CONTAIN ENOUGH LAUNDRY TIME TO SUPPORT CREST'S
PUBLISHED CYCLE COUNTS, AND THE SHORTFALL IS THREE TIMES WIDER IN ITALY THAN IN SPAIN.** Eligible
laundry minutes per dwelling-year: **es 2,462 / uk 1,589 / it 781**, against a washing machine that
asks 195.91 cycles × 138 min = **27,036 minutes**. Modelled/published 0.776 / 0.179 / 0.092.
🔴 Laundry is the archetypal SECONDARY activity, and `D-S9-1` ruled primary-only — so
`FINDING 139` is the size of what that ruling costs, and the two belong together in the methods.

🟢 **`FINDING 140` — THE THREE-DIGIT CORPUS DECISION BUYS EXACTLY ONE PUBLISHED
DISTINCTION.** `G9.11` PASSES, 6 signatures against 5 on CREST's electricity rows alone, and the
single split is **ACL 331 Laundry against 332 Ironing** inside group 33. The splits in groups 03 and
31 are ours. 🔴 Do not read the pass as vindication: `RL25` stands, and the corpus decision is
still best justified on microdata fidelity.

🔴🔴 **`FINDING 141` — THE DIARY DAY STARTS AT 04:00 AND STEP 8's SCHEDULES WERE
WRITTEN AS IF IT STARTED AT MIDNIGHT.** `D-S2-5` harmonised every diary onto a 04:00 origin;
`4thJ_step7_schedules.py` writes minute 0 into a `Schedule:File` that EnergyPlus reads from midnight.
**Step 8's 13,108 runs applied occupancy four hours early.** Confirmed on three independent
artefacts: the Step 2 ruling and its code, the generated diaries (sleep 0.99 at indices 0-2, waking
at 3-5), and the shipped Step 8 presence files (trough at index 7). 🟢 Step 9 is corrected by
one cyclic shift of the whole year series, stamped `"rotated_to_midnight": true`. 🔴 Step 8 is
the author's call — `D-S9-3`, recommendation (a), about 13,108 local runs.

🟢 **`FINDING 142` — THE APPLIANCE PEAK FALLS SIX HOURS APART ACROSS THE THREE COUNTRIES.**
Spain **14:00** (503 W), Italy **18:00** (404 W), Britain **20:00** (416 W), one appliance set and
one calibration; the only thing that differs is the diary. This is the step's positive result and it
is also why `G9.12` fails — CREST's statistics are UK-2000.

⚪ **The campaign is on the SAME dwellings Step 8 simulated, proven rather than assumed**: the
trigger rebuilds them through `4thJ_step7_schedules.py` and refuses to run unless all 100 presence
schedules reproduce the shipped CSVs byte-for-byte. 100/100 in every fold. Electricity
**2,244 / 2,085 / 2,065 kWh per dwelling-year**; DHW **200.79 / 201.01 / 199.47 l per dwelling-day**,
which reproduces Jordan & Vajen's Table 1 to better than 1 % on all four event categories.

⚪ `prereg.md` does not cover Step 9; its md5 `e4243e07cdd80c9c846b91f40e3e8c45` is unchanged.

---

### 2026-08-26 — `D-S9-3` RULED **(a)** AND EXECUTED; STEP 9 RE-RUN END TO END AND **NOTHING CHANGED**

🟢 **`FINDING 141`'s open call is closed.** The author ruled **(a) re-emit and re-run**: all 13,108
Step 8 runs were rebuilt on schedules rotated to midnight. The full record of that campaign, and of
what it did to the Step 8 results, is
`Step8_docs/docs/2026-08-26_D-S9-3a_the-rotated-re-run.md` — 🔴 **read it before quoting any Step 8
number.** The short version: **no occupancy claim survives on either channel**; what survives is the
dwelling-class ordering and the fixed annual peak hour.

🟢 **Step 9 itself is unaffected, and this was verified rather than assumed.** Step 9 already
rotated internally (`"rotated_to_midnight": true`), so the prediction was that a full re-run would
reproduce the tree bit-for-bit. The tree was snapshotted (630 files), then
`4thJ_step9_trigger.py --fold es|uk|it`, `4thJ_step9_aggregate.py` and
`4thJ_gates_step9.py --root . --offline` were re-run in order. **`diff -rq` between the snapshot and
the re-built `outputs_step9/` printed nothing and exited 0 — the trees are identical.** The three
triggers reproduced their own numbers to the digit: electricity **2244.1 / 2084.7 / 2065.4 kWh per
dwelling-year**, DHW **200.79 / 201.01 / 199.47 l per dwelling-day** and **98.43 / 111.67 /
94.09 l per person-day**, `campaign run True` in every fold.

🔴 **`FINDING 149` — THE BOARD IS 15 PASS / 3 FAIL / **1 NOT CHECKED**, AND THE "16 PASS /
3 FAIL" WRITTEN ON 2026-08-25 COUNTED THE NOT CHECKED GATE AS A PASS.** The runner's own tally line
reads `counts: {"FAIL": 3, "NOT CHECKED": 1, "PASS": 15}`, and `G9.4` is the NOT CHECKED one —
two of three DOIs do not resolve. **That is precisely what `V9.c` exists to forbid**, and the prose
did by hand what the checker refuses to do by code. The **per-gate verdicts have not moved**; only
the sentence that summed them was wrong. Every "16 PASS / 3 FAIL" in this document and in
`4thJ_09_enduseLoads_val.md` is superseded by **15 PASS / 3 FAIL / 1 NOT CHECKED**. No gate was
touched to produce this correction.

⚪ **The per-gate board is unchanged.** The same three fail for the
same registered reasons — `G9.6` against CREST's published cycles per year, `G9.7` against the
registered 30–50 l/person/day band (`es` median 100.16, `it` 91.06, `uk` 117.65), `G9.12` on R²
below 0.85 in all three folds (0.2967 / 0.4106 / 0.0346) — and `G9.4` is **NOT CHECKED** because two
of three DOIs do not resolve and `V9.c` forbids reporting that as PASS. **No threshold was moved and
no checker was edited**; `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched.

⚪ **What this null is worth.** A re-run that changes nothing is the only evidence that Step 9's
internal rotation was already correct and that the Step 8 fix did not leak into it. It is reported
here because it was measured, not because it was expected.
