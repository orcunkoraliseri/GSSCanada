# V4-B3 — 🔴 WITHDRAWN: `B-13` does not reach the submitted 2J manuscript, and that was settled on 2026-08-04

**2026-08-06 · desk work · read-only · nothing was sent anywhere.**

**The premise of this task is false.** V4-B3 was written as *"a transform present in the submitted
pipeline is described in neither manuscript"*, with a hard stop of **2026-08-13** after which a
notification would go out. **There is nothing to notify.** The question was investigated to a
conclusion two days before v4 opened, and the finding was withdrawn as paper-facing then.

---

## 1. What `V2-A1` established on 2026-08-04

| step | result |
|---|---|
| **the transform is real** | `occPre × (occDensity + 1)` then `.clip(upper=1.0)` exists in `21CEN22GSS_occToBEM.py`, and the over-count is genuine — `occDensity` sums `social_sum` across household members (`21CEN22GSS_HH_aggregation.py:177-178`), so two co-residents who each report the other are counted twice |
| **the magnitude was measured** | On 41.35 M slot-rows: `occDensity+1 > HHSIZE` in **14.3 %** of rows (**27.1 %** for two-person households); the clip binds on **15.9 %** of occupied slots; mean \|Δ\| vs the max rule = **0.232** schedule units = **32.55 % of person-hours** — **32× the pre-registered 1 % materiality threshold** |
| 🔴 **but that converter does not ship** | The production converter behind the submitted manuscript is `2J_docs_occ_nTemp/07_aug_to_bem.py` (2026-07-13). Its `convert()` computes `occ48 = groupby(...)[HOM].mean()` at `:97`. **No `occDensity`, no `social_sum`, no `×(density+1)`, no `.clip()` anywhere in the file** |
| **verified on the artefact, not on code reading** | The shipped `BEM_Schedules_2022.csv` (673 MB, 2026-07-09 — the relink date the manuscript cites) carries occupancy values in steps of 1/12, 1/10, 1/8, 1/24 — **a fraction of members**. A max rule yields only {0, 1}; the `occDensity` rule yields a clip-saturated mass at exactly 1.0. **Neither is what ships.** The legacy output was retired 2026-05-31, **before submission** |

**So the magnitude V4-B3 set out to establish already exists — 32.55 % — and it applies to a converter
the paper does not use.** The deadline was set to force a measurement that had already been made, for a
disclosure that had already been shown not to be owed.

🔴 **`V2-A1`'s own pre-registered risk — *"V2-A1 finds B-13 is material → touches a submitted
manuscript"* — was recorded as NOT having materialised.** V4-B3 reinstated exactly that risk as fact.

---

## 2. And the manuscript already says the right thing — I checked the text

`V2-A1` did find one genuine clarity defect: §3.3's *"occupied if any member is present"* and §3.5's
*"occupancy (AT_HOME fraction)"* sit three paragraphs apart and can be read as a contradiction.
`V2-A2` drafted a clause. **It landed.** `2J_docs_occ_nTemp/writing/fullSet/readySubmission.md:231`
now reads:

> *"The occupancy channel is the per-slot **mean** AT_HOME indicator across household members — the
> fraction of the household present in each slot — and is computed **independently** of the per-slot
> maximum used for household formation in §3.3, which serves only to define dwelling-level occupancy
> for the plausibility gate and **does not propagate to the injected schedule**."*

**That is a direct, explicit description of the transform that actually ships, and an explicit
disambiguation from the one that does not.** The premise *"described in neither manuscript"* is false
of the current text.

---

## 3. ⚠️ The one thing that genuinely survives, and it is small

**The clause is in the `.md` only. It is in no `.docx` on this machine.** Checked by unpacking
`word/document.xml` and searching:

| file | date | *"per-slot maximum AT_HOME"* | *"computed independently of the per-slot maximum"* |
|---|---|---|---|
| `writing/fullSet/readySubmission.md` | **2026-08-04 17:55** | yes | ✅ **yes** |
| `writing/fullSet/previous/readySubmission.docx` | 2026-07-15 | yes | ❌ **no** |
| `writing/resources/submission_Occ_NUsJournal.docx` | 2026-06-11 | no | ❌ no |

`V2-A2` recorded this itself — *"clause in both `.md`; `.docx` **N/A**"*. The clause was written
**2026-08-04**, and every `.docx` on disk predates it.

⚠️ **So if the journal holds a `.docx`, it holds the version with the two conflatable sentences and
without the disambiguation.** **I cannot determine from file dates which artefact was submitted or
when** — these are local build times, not submission records.

**This is a clarity item for the next revision round, not an erratum.** Nothing in it is wrong; two
sentences are separable in the local copy and possibly not in the journal's. **It is the user's call
whether it is worth raising, and there is no deadline on it** — the thing a deadline was justified for
does not exist.

🔁 **Reopen trigger.** If a revision request arrives, check that the §3.5 clause is carried into
whatever file is returned to the journal. **If the submitted artefact turns out to be the `.md`, this
item closes with nothing owed at all.**

---

## 4. What this cost, and the pattern it belongs to

**`V4-B3` is the second of the four decisions taken on 2026-08-06 to be withdrawn as never-open**, the
other being `V4-B1` (decided in `V2-B4` and executed in `V2-D10` on 2026-08-05).

🔴 **Both were written into v4 from prose — the audit document, memory files, superseded prompts —
and in neither case was the v2 plan re-read before the item was called open.** `V2-A1`'s closure is at
`3rdJ_L3_v2_implementation.md:367` and its Progress Log entry is titled, in full,
*"V2-A1 — the B-13 falsifier — **DONE. B-13 does NOT reach the submitted paper.**"* The v2 closure
prompt states it in six words: ***"B-13 withdrawn (no 2J erratum owed)."***

**v4 existed because open items were prose and not tasks. It then turned prose into two tasks that were
already finished** — and, worse, **put both to the user as decisions**, spending their attention on
questions that had answers. **The reading defect was in me, not in the record: the record was explicit,
indexed and one grep away.**

**Rule adopted, and it is a `j4_ledger_check` candidate rather than a resolution:** *a new round may
not open an item that names a `B-*`, `C-*` or `G-*` audit finding without quoting that finding's
terminal status row from `3rdJ_L3_v2_implementation.md` §"every finding carries a terminal status".*
The status table exists — `B-13`'s row is at line 1269 — and it was not consulted.
