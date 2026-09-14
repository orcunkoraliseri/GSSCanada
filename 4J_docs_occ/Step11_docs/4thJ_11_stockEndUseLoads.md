# Step 11 — Activity-driven end-use loads at stock scale

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 11. Validation: `4thJ_11_stockEndUseLoads_val.md`
#### Basis: `../Step10_docs/4thJ_10_nocoreRealStock.md` — Step 10 campaign `C2` (no-core), the campaign this step will run on. Core-era campaign `C1`, closed and archived: `../Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md`. Predecessor (closed): `../Step9_docs/4thJ_09_enduseLoads.md`

---

## STATUS

⚪ **PLANNED, 2026-08-26. Nothing built.** Depends on Step 10, which depends on the OpenUBEM
European-locations arc.

🟢 **Work item 11.2 is DONE, 2026-08-27** — the only item in this step that needed nothing from
Step 10. Record: `docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`. It raises `D-S11-1` and
findings `163`–`166`, and it **blocks `G11.7`**: that gate inherits `G9.7`'s 30–50 band verbatim and
must not be scored until `D-S11-1` is ruled. 🟢 **RULED THE SAME DAY, (d)(ii) → (b):
`G9.7` and `G11.7` are both `INFO`, permanently; the band is inherited UNMOVED and the deviation is
reported, not scored. `G11.7` is no longer blocked — it is classified, and it will not be run at
stock scale.** The ruling is §8 of that record and what was executed against it is §9.
🔴 **`D-S11-2` is now open in its place:** the ruling left `scale_dhw_by_2` with no
detector anywhere in Step 9, and the replacement arm is a band decision, so it waits for the
author. 🔴 **§1.3 below is SUPERSEDED by that record** — its
named candidate was refuted; read §1.3a beside it.

🟢 **CORRECTION, added additively 2026-08-28 — the two sentences above are STALE and `D-S11-2` is
NOT open.** It was **discharged on 2026-08-27**, the same day it was raised, by gate `G9.15`: stock
means **200.79 / 201.01 / 199.47** l/dwelling/day against 200 ± 10 %, medians **174.97 / 175.79 /
195.13** printed, the gate **seen failing** at **401.58 / 402.03 / 398.93** on doubled draws, and the
battery re-run **13 HIT / 0 MISS / 2 already-failing**. Record: `Step9_docs/4thJ_09_enduseLoads_val.md`;
the work-item table at §11.2 already carries the closure and this STATUS paragraph did not. ⚪ Nothing
above is deleted — the stale sentences are kept as the record of what was carried, and this line is
what governs. 🔴 **No decision from Step 11 is waiting on the author.**

🔴 **Step 9 is CLOSED and this step does not reopen it.** Step 9's board is
**15 PASS / 3 FAIL / 1 NOT CHECKED** (`FINDING 149`); its mapping, its trigger, its citations and its
thresholds are read-only from here.

🟢 **`Basis:` path repaired 2026-09-07, on the author's instruction, and this is the record of
what it said before.** The header read `Basis: ../Step10_docs/4thJ_10_ubemRealStock.md`, written
before `D-IMP-4` (2026-09-03) archived the core-era campaign. That file now lives at
`../Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md`, so the literal path had stopped
resolving. ⚪ It was the **only live dangling pointer** to the moved `C1` documents: the other
twelve references found in the same audit are closed records — `IMP/docs/DONE/` dockets,
`Step10_docs/impl/` ledgers, sent `messages_OpenUBEM/` files, run deep-research prompts and their
vetting — and those are **deliberately not rewritten**, which is what `Step10_docs/README.md`'s
redirect table exists for.

🔴 **The repair also names the right campaign, which the old line could not.** Step 10 now has
two: `C1` (core-era, run, scored, **archived and not reported**) and `C2` (no-core, **the one Step 11
will run on**, spec only, gate series `G10N.x`). The header now points at `C2` and keeps `C1`
addressable beside it. ⚪ **Nothing else in this step moves.** Section 2.1's note still governs
the content: what is written below still describes `C1`'s core-era population until a no-core `C2`
cell exists. No gate is re-scored, no band moves, and Step 11 remains **PLANNED, nothing built**.

🟢 **CLOSURE, 2026-09-13 (last+264) — EVERY SENTENCE ABOVE THAT SAYS `PLANNED` OR
`NOTHING BUILT` IS NOW STALE, AND THIS PARAGRAPH GOVERNS.** Step 11 is **COMPLETE**. It was built and
run between last+229 and last+263, and the Progress Log below was not kept during that stretch — the
record lived in `docs/` and in `Prompts/RESUME.md` instead. ⚪ **Nothing above is deleted**; the stale
sentences stay as the record of what was carried, exactly as the 2026-08-28 correction did.

**Work items:** `11.1` `11.2` `11.4` `11.5` `11.6` **DONE**; `11.3` **DONE** (built at last+46,
`docs/2026-09-08_work-item-11.3_trigger-campaign-runner-built.md`; run at full size in both cities at
last+236); `11.7` **WITHDRAWN** (`Prompts/RESUME.md` §6 — withdrawn on the model's own judgement, the
author did not object; it renders a stock aggregate and is **a rendering, never a result**).

**Board:** all **18** declared `G11.x` gates scored, `V11.g` **SUITE COMPLETE**,
`{"PASS": 14, "FAIL": 2, "INFO": 1, "NOT CHECKED": 1}`.
🔴 **`G11.6` FAIL** (per-appliance activation counts outside CREST ±15 %) and
🔴 **`G11.12` FAIL** (stock diurnal shape, R² 0.4347 `uk` / 0.0781 `it`) are **one single
mechanism, not two defects**: CREST's reference profile is >77 % laundry at 11:00 while this model
suppresses laundry starts 80–90 % under the already-ruled **`D-S9-1`** — only *primary* HETUS
activities trigger appliances, and laundry is recorded as a *secondary* activity. **Both stay FAIL, no
code change, band never moved**, consistent with `G9.6`/`G9.12`'s own Step 9 FAILs. `G11.7` stays
permanently `INFO` (`D-S11-1`). `G11.4` is `NOT CHECKED` offline — 3 of 4 DOIs need network; not a defect.
🟢 **`G11.8` and `G11.18` are genuine new stock-scale PASSes** (DHW event mix within 3 pp of
Table 1; stock mean DHW **202.41** `uk` / **200.35** `it` l/dwelling/day against 200 ± 10 %).

**Battery:** **18 HIT / 0 MISS / 1 already-failing** (`G11.6`, `ALREADY_FAILING_AT_BASELINE`, `V11.b`),
**COVERAGE CLAUSE PASS**.

🔴 **Step 11 is the LAST step of the pipeline.** `D-IMP-4` (2026-09-03) deleted Step 12 — *“The
pipeline is Steps 0–11.”* **Nothing downstream consumes Step 11's `appliance_electricity`/`dhw`
output**; what follows is cross-step analysis and the manuscript, not another computed step.

---

## AIM

Run Step 9's mapping and trigger — **unchanged** — on Step 10's per-dwelling real-stock population, so
that the stock-scale claim Step 9 could only *declare* is finally **tested at the scale the source models
were validated at**.

---

## 1. WHY THIS STEP EXISTS — AND WHY IT IS NOT A SECOND CHANCE

Step 9 shipped three FAILs and moved no band:

| gate | verdict | the number |
|---|---|---|
| **`G9.6`** trigger rate | **FAIL 60** | `FINDING 139`, saturation; 3 standby-only devices `NOT_EVALUABLE` |
| **`G9.7`** DHW volume | **FAIL 300** | medians **100.16 / 117.65 / 91.06** L/person/day against a registered **30–50** band |
| **`G9.12`** stock-scale agreement | **FAIL 3** | R² **0.297 / 0.411 / 0.035** against **0.85** |

🔴 **Step 11 does not exist to make those pass.** `G11.6`, `G11.7` and `G11.12` inherit the same bands,
unmoved. If they pass at stock scale, that is a **scale effect** and it is a result; if they fail again,
Step 9's failure is confirmed as a property of the mapping and the paper says so. Re-measuring a failing
quantity on a bigger denominator and reporting whichever answer is nicer is the one thing this step must
not become.

### 1.1 🔴 The one place scale genuinely changes the question — `G9.12`

Step 9's `9C` states the bound the whole downstream claim rests on: the published activity-to-load models
(CREST, Widén, LPG, RAMP) validate against **aggregate** demand at **100–500 dwellings**, feeder or
district scale, R² above 0.90; **individual single-dwelling prediction has high residual variance** and
is not claimed.

Step 9 scored `G9.12` on **100 dwellings per fold** — *exactly at the registered `≥ 100` floor*. The gate
was therefore evaluated at its minimum admissible population, which is the weakest configuration in which
it could have been evaluated at all. Step 10's neighbourhoods carry roughly **1,200 residential buildings
per site** (Madrid, London, Bologna), each with `N_u` dwellings in Arm D. **Step 11 is the first
configuration in this project that sits inside the range the source models were validated in** — so
`9C`'s caveat becomes *satisfiable* rather than merely *declared*. That is Step 11's honest contribution,
and it is worth stating plainly because it is smaller than "we fixed R²".

### 1.2 🔴 But the population changes too, and that is not a free comparison

Step 9's 100 dwellings were drawn **across a fold**. Step 11's dwellings sit in **one neighbourhood** —
spatially adjacent, on one weather file, in a correlated construction-epoch mix. These are **not the same
population**, and an R² computed on one is not comparable to an R² computed on the other without saying
so. Every stock-scale statistic in Step 11 names its population, its spatial extent and its weather file
(`G11.16`). A cross-population R² comparison presented without that declaration is a **FAIL**, not a
footnote.

### 1.3 🔴 `G9.7`'s failure is a magnitude error, and scale will not fix it

> 🔴 **SUPERSEDED 2026-08-27 by `docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`. Read §1.3a
> before quoting anything below.** The section's conclusion — *scale will not fix it* — is
> **confirmed**, and now has a mechanism. Its named candidate is **refuted**. The paragraphs are
> kept unedited because they are the brief 11.2 was scored against.

The DHW medians are **2–4× the registered band** (100.16 / 117.65 / 91.06 against 30–50). A factor of two
to four is not the shape of a small-sample artefact; it is the shape of a definitional or unit error, or
of a genuine disagreement about what the band's basis is — Step 9 recorded it as *"a band whose basis its
own source does not define"*.

**Work item 11.2 is therefore a diagnosis of `G9.7`, performed on the Step 9 artefact, before Step 11
re-measures anything.** Candidate explanations must be **falsified rather than assumed** — a per-person
versus per-dwelling denominator, a 60 °C versus delivered-temperature basis, an event-duration or
flow-rate unit, or a real disagreement with Jordan & Vajen's population. Carrying an undiagnosed 2–4×
error into a stock-scale campaign does not test it; it just moves it to a bigger denominator and gives it
a smaller confidence interval.

#### 🔴 A named candidate already exists in this project's own vetted research, and it is cheap to falsify

`DeepResearchPrompts/RL25_activity_to_appliance_mapping.md` §B10 records Jordan & Vajen's IEA Task 26
parameters as: **base 50 L/person/day at 60 °C**, with the four events **short 1–2 L at 60 °C**,
**medium 6 L at 60 °C**, **bath 100–140 L at 40 °C**, **shower 30–50 L at 40 °C**. Its §C adds the
distinction explicitly — *"Jordan & Vajen specifies 50 L/person/day at 60 °C (not delivered 40 °C)"*.

Set against `G9.7`'s registered band of **30–50 L/person/day at 60 °C**, two things stand out:

* the band's **upper edge, 50, is the source's base daily value**, not the top of a range — so the band
  reads like a **±** interval placed around a single published figure; and
* **`30–50` is also, exactly, the shower event's volume — at 40 °C.** A band and an event row carrying the
  same two numbers on two different temperature bases is precisely the coincidence that produces a
  silent unit error.

**Hypothesis to falsify (not a conclusion):** Step 9's measured medians are **delivered-volume** sums
(bath 100–140 L and shower 30–50 L at 40 °C dominate the total) compared against a **60 °C-equivalent**
band. On a 10 °C inlet that is a factor of `(40−10)/(60−10) = 0.6` in the wrong direction — which turns a
compliant 60 °C total into a delivered total roughly **1.67×** larger, and stacks with any per-dwelling
versus per-person denominator error to reach the observed **2–4×**.

🔴 **This is a lead, not a finding.** `RL25` is a deep-research report and this project's standing rule is
that such reports carry fabricated citations until vetted — `FINDING 47` caught exactly that in this
literature, on three counts at once. **Work item 11.2 must read Jordan & Vajen (2001) IEA Task 26
Table 2.1 directly** and check Step 9's own conversion code, before either confirming or discarding this
explanation. What matters here is that 11.2 starts with a **named, checkable candidate** rather than a
blank page — and that no band moves either way.

### 1.3a 🟢 What 11.2 actually found, 2026-08-27 — and what the author ruled on it

> 🟢 **RULED 2026-08-27, `D-S11-1` (d)(ii) → (b).** `G9.7` and `G11.7` are `INFO`,
> permanently, on the `G8.7` / `D-S8-5` item 1 (a) precedent. 🔴 **The band is
> inherited UNMOVED at 30-50 L/person/day and the medians are still printed as outside it** — the
> comparison is reported as a denominator incompatibility, not scored as a model failure. Fuentes
> et al. (2018) is now cited, and `G9.4` caught an issue-number error in the citation on its first
> online run (`FINDING 167`). 🔴 **`D-S11-2` is open:** the ruling left
> `scale_dhw_by_2` undetected by the whole Step 9 battery, seen by doubling every `dhw_*` column
> and watching `G9.7` return `INFO` anyway. The repair that invents no number — a per-dwelling arm
> at Jordan & Vajen's own 200 l/day — is a band decision and was deliberately not made here.
> Executed in full: §9 of `docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`.

🟢 **The quoted block above is the ruling AS IT STOOD; `D-S11-2` did not stay open.** It was
discharged the same day by `G9.15` — the per-dwelling arm at Jordan & Vajen's 200 l/day, implemented
and **seen failing** on doubled draws. See the correction in §STATUS for the measured figures.

Full record: `docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`. Four findings, no band moved, no
checker edited, no artefact regenerated.

🔴 **`FINDING 163` — the band is not Jordan & Vajen's.** It enters this project at `RL13` row 15
(2026-08-14, **Tier 2**), which attributes *"30 to 50 L/person/day at 60 deg C"* jointly to
Jordan & Vajen **and to Fuentes et al. (2018)**, *A review of domestic hot water consumption
profiles…*, RSER 81(1): 1530–1547, DOI `10.1016/j.rser.2017.05.229`. §9B of
`4thJ_00_HETUS_LLM_Pipeline.md` compressed that row to a single attribution, Step 9 registered
`G9.7` on the compressed sentence, built the model on Jordan & Vajen's table, and cited **only
Jordan & Vajen**. **The gate scores a review paper's per-person band against a tapping model's
per-dwelling volumes, and the review paper is in no citation table in this project.** ⚪ Fuentes has
**not been fetched**; the 30–50 figure is named, not verified.

🔴 **`FINDING 164` — the temperature candidate is REFUTED, not unconfirmed.** The report's table has
**no temperature column**, and the paper says outright *"for the cold water temperature distribution
during the year, a local profile should be used."* Its only temperature is a **35 K** rise in two
worked maximum-energy examples. There is no delivered-vs-60 °C conversion to have got wrong. ⚪ And
granting `RL25`'s unsourced per-category temperatures anyway gives **×0.800**, not the ×0.600 §1.3
assumed — bath and shower are exactly half the daily volume, not the dominant share — which leaves
`es` at **80.12**, still outside the band.

🔴 **`FINDING 165` — `G9.7`'s scored quantity is `200 / n_members`, so it is a test of household
size.** The per-person column reproduces `dhw_litres_per_day ÷ n_members` to **0.0005 over all 300
rows**, and the emitted volume does not depend on household size by `D-S9-2` item 5 (a). The band is
therefore satisfiable for and only for households of **4, 5 or 6 people** — **7 / 4 / 9 of 100**
dwellings in `es` / `uk` / `it`, whose medians are all **2.0**. `es`'s 100.16 *is* `200 / 2`.
🔴 **This is why scale will not fix it: there is nothing stochastic left to average down.**
`11.5` must not re-measure `G9.7` at stock scale.

🔴 **`FINDING 166` — `RL25` §B10's volumes are all sound; its bases are all invented.** Short 1–2 L
(source 1), medium 6 L (6, exact), bath 100–140 L (140), shower 30–50 L (40) — **4 of 4 consistent**;
the per-category temperatures and the 50 L/person/day base — **2 of 2 absent**. `FINDING 138` applied
a string-match test where an equivalence test was needed. Its load-bearing half stands.

🔴 **`D-S11-1` is raised** and adds an option `D-S9-2` item 7 could not have: **(d)** cite the band's
real source and score it on its real basis. Recommendation **(d)(ii) → (b)** — repair the citation,
then make the gate a permanent `INFO` on the `G8.7` precedent, with (a)'s reporting. **The band moves
under no option.**

🔴 **`G11.7` is BLOCKED.** It inherits the 30–50 band verbatim and must not be scored before
`D-S11-1` is ruled, or Step 11 reproduces the same comparison at a bigger denominator — the exact
failure §1.3 was written to prevent.

### 1.4 🔴 A failing gate's perturbation demonstrates nothing

Step 9 recorded this correctly and Step 11 inherits it: `G9.6`, `G9.7` and `G9.12`'s registered
perturbations were reported **`ALREADY_FAILING_AT_BASELINE`**, never as hits, because a mutation cannot
be seen felling a gate that is already down. Any `G11.x` inheriting a failing Step 9 gate carries the same
disposition until the underlying quantity passes at baseline.

---

## 2. WHAT IS CARRIED ACROSS UNCHANGED

* **The mapping is not re-authored.** `activity_appliance_map.csv`, its citations, its VALIDATED /
  NOT VALIDATED labels and their scales carry over as-is. `G11.1`–`G11.4` re-score the same rows against
  the same bars. 🔴 Step 9's `9A` is the reason: *we adapt CREST / Widén / LPG / RAMP; we do not author a
  new heuristic*, and an ad-hoc mapping is the single easiest thing in this paper for a reviewer to
  reject.
* **The trigger fires from the primary activity code alone.** `act2` remains **calibration-only** and must
  not appear among the trigger's runtime columns (`G11.14`). 🔴 A trigger reading an absent column does
  not raise — it silently never fires.
* **No per-dwelling prediction.** `G9.13` → `G11.13`, unchanged: no result in any output, table or figure
  is a per-dwelling prediction, asserted by a search over the results artefacts.
* **The assignment check.** `G9.9` → `G11.9`: re-open the **saved IDF** and assert every
  `WaterUse:Equipment` object still points at the schedule it was built with. 🔴 A value check cannot see
  a re-pointed object — in 3J that hid a ×3.028 draw increase across 56 cells with zero violations
  reported.

### 2.1 🔴 Added 2026-08-26 (evening) — the Step 10 arm label must survive aggregation

Step 10 runs two populations that are **never pooled** (Step 10 §6.1): **Arm D**, dwelling-partitioned,
and **Arm F**, `one_zone_per_floor`. Step 11 aggregates over buildings, and an aggregation is exactly
where an arm label gets dropped.

🔴 **`RL29` sharpened why this matters, and the sharpening survived vetting.** The `one_zone_per_floor`
fallback is not a *noisier* estimate of the same quantity — it spatially averages non-coincident gains
across dwellings, so it **under-predicts** heating demand and peak power **systematically, in one
direction**. That changes what an Arm F total is allowed to be called:

* An Arm F stock total is a **lower bound**, and saying so is a publishable statement.
* Calling it an estimate is not, because the error has a known sign and an unknown size.

⚪ **Direction only. The magnitude is refused.** `RL29`'s figures (−5…−15 % annual, −10…−25 %
peak, and an `N_u` error ladder) all rest on `[R2]`, whose own CrossRef line returns a **different paper**
than the one cited. The bias *direction* stands on Chen & Hong (2018), which is correctly cited; the
numbers do not stand at all and may not be quoted. (`../DeepResearchPrompts/VETTING_RL28_RL29.md` §1.7.)

Enforced by `G11.16`, extended: the population declaration now carries the **arm**, and `G11.17` refuses
any Step 11 aggregate that mixes them or that presents an Arm F total without the bound language.

> 🟡 **Added 2026-09-03 (`D-IMP-1`, no-core review, I-1).** Arm F is **redefined** for the no-core
> regime: **check-FAIL or unusable footprint → one box per floor**, no longer a convexity refusal
> alone (any layout-route failure now falls back to one box per floor, per
> `IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` and
> `Step10_docs/4thJ_10_nocoreRealStock.md` §3.2). `G11.17` above is **unchanged** — the LOWER BOUND
> rule and the never-pooled rule apply identically to the redefined Arm F. Nothing built; this
> section still describes Step 10 campaign `C1`'s core-era population until a no-core `C2` cell
> exists.
>
> 🟢 **Corrected 2026-09-03 (`D-IMP-4`), same day.** The path above first read
> `Step12_docs/4thJ_12_nocoreRealStock.md`. **There is no Step 12** — the pipeline ends at Step 11
> and the no-core campaign is **Step 10 campaign `C2`**, gate series **`G10N.x`** (formerly
> `G12.x`); the core-era campaign `C1` is archived at `Step10_docs/archive_C1_core_era/`, closed
> and unchanged. Docket: `IMP/docs/DONE/2026-09-03_D-IMP-4_no-step-12-fold-into-step-10.md`.
> Nothing in Step 11 moves.

---

## 3. 🔴 THE DOUBLE-COUNTING SEAM WITH STEP 10

Step 10 reports on OpenUBEM's **simulated vs reconstructed** EUI framework: `EUI_reconstructed =
EUI_sim + EUI_service_loads`, where the service loads (DHW, cooking, distribution parasitics) are
*reconstructed* from TABULA Table-4 national end-use shares because EnergyPlus did not simulate them.

**Step 11 supplies those same end-uses from the diaries.** If Step 10 reconstructs DHW *and* Step 11
simulates it, the pair double-counts, and the double count is invisible in both artefacts individually.

> **Rule.** For any building where Step 11 supplies an end-use, Step 10's reconstruction **must not also
> add a Table-4 share for that end-use**. The accounting path is chosen **once**, per end-use, per
> building, and recorded in the manifest. End-uses appearing in both paths: **0** (`G11.15`).

⚪ This is also what the OpenUBEM side means by *"the refusal to reconstruct DHW on an incomplete base"*
(MVP §12.11) and by caveat **C-01**. The register travels with the numbers.

---

## 4. WORK ITEMS

| # | Item | Depends on | Simulation? |
|---|---|---|---|
| **11.1** | 🟢 **DONE 2026-08-27. Carry-over audit** — the Step 9 mapping, trigger and citation set re-scored unchanged on the new basis; `G11.1`–`G11.4`. Online **`PASS 61 / PASS 192 / PASS 149 / PASS 4`**, offline the same with `G11.4` `NOT CHECKED` (`V11.c`); the other fourteen gates print **`NOT RUN` by name and no tally** (`V11.g`). Battery **7 HIT / 0 MISS**, coverage clause PASS. 🔴 **`FINDING 168` found in the doing: `G11.15` headed two gate-table rows; the DHW newcomer moved to `G11.18` and a duplicate-ID census is now a registered detector.** ⚪ `G11.14` is deliberately NOT in scope — it asserts the trigger's columns against the **generated diaries**, and Step 11's are Step 10's, which do not exist yet. Record `docs/2026-08-27_work-item-11.1_carry-over-audit.md` | Step 9 artefacts | no |
| **11.2** | 🟢 **DONE AND RULED 2026-08-27. `G9.7` diagnosis** — falsify candidate explanations for the 2–4× DHW magnitude **before** re-measuring (§1.3). Candidate refuted, mechanism found, `D-S11-1` raised and **ruled (d)(ii) → (b) the same day**: `G9.7` and `G11.7` are permanent `INFO`, band unmoved, citation repaired, `FINDING 167` found by `G9.4` in the doing. 🟢 **`D-S11-2` raised AND closed the same day: `G9.15` implemented, `G11.18` declared** (§1.3a, §§9-10 of the record) | Step 9 artefacts | no |
| **11.3** | 🟢 **DONE. Per-dwelling trigger campaign** — run the trigger on Step 10 Arm D's `N_u` diaries per building. **Built 2026-09-08** (`tools/4thJ_step11_trigger_campaign.py`; every refusal seen failing with a passing control; `SCORES NOTHING` by design) — record `docs/2026-09-08_work-item-11.3_trigger-campaign-runner-built.md`. **Run at full size 2026-09-12 (last+236)**, `--diary-diversity reseed`, no `--limit`, zero refusals, zero errors: **Bologna 29,902 flats / 1,126 buildings** (6,126.2 s) → `outputs_step11/c2_it/step11_11-3_it_reseed.json` (33.8 MB, `n_flats_enumerated == n_flats_run == 29902`, `smoke_run: false`); **London 7,602 flats / 1,200 buildings** (1,537.3 s) → `outputs_step11/c2_uk/step11_11-3_uk_reseed.json` (9.0 MB, same clean counts). 🔴 **A seam was found mid-launch and ruled by the author:** 42 Bologna + 7 London buildings carry synthetic *floor-averaged* diaries, not real per-flat Step 7 diaries, so the per-flat diary check correctly refused them; the author chose **EXCLUDE** — all **49** buildings are flagged *no Step 11 data*, never scored, never guessed at, the same way the 3 accepted courtyard buildings are. Non-destructive method: filtered **copies** of each city's `cells/`, 420 IT + 70 UK cells dropped, skip counts matching the exclusion lists exactly; **nothing in Step 10's output was touched**. ⚪ Madrid (ES) was never in scope for this campaign. | Step 10 items 10.4, 10.6 | no |
| **11.4** | 🟢 **DONE 2026-09-13. Accounting-path resolution** — one path per end-use per building, recorded in the manifest (§3). **Closed on 11.3's OWN construction, not new work**: `STEP10_END_USES`/`STEP11_END_USES` are a fixed disjoint partition, `check_seam` (`S10`) refuses any overlap or unknown end-use before any manifest is written (seen refusing on a planted overlap 2026-09-13), and `population_declaration()`'s `accounting_paths` field records the partition in every manifest — verified present, byte-identical, in both cities' real last+236 output. The 49 buildings excluded from Step 11 have `appliance_electricity`/`dhw` on NEITHER path (declared absent, not zero) — not a seam violation, recorded for 11.5. Record: `docs/2026-09-13_work-item-11.4_accounting-path-closure.md` | 11.3, Step 10 10.6 | no |
| **11.5** | 🟢 **DONE 2026-09-13. Stock-scale aggregation** — `G11.12` at real neighbourhood scale, with the population declaration `G11.16` requires. New tool `tools/4thJ_step11_aggregate.py` imports (never re-implements) 11.3's trigger loop and `G9.12`'s own scorer, accumulating `elec_ts`/`dhw_ts` elementwise across every drawn flat into one stock diurnal profile — never persisting per-flat series at 30k-flat scale. 2,000-flat Bologna smoke ran clean first (`FAIL R2=0.0731, n=2000`, correctly flagged as a smoke, not carried forward). Both full populations then run to completion, no `--limit`, `reseed` unchanged: **London 7,602 flats/1,200 buildings, `G11.12` FAIL R2=0.4347**; **Bologna 29,902 flats/1,126 buildings, `G11.12` FAIL R2=0.0781**. Same gate Step 9 already FAILED at n=100 (§2) — two independent stock populations failing the same way is evidence the measurement is real, not a defect to chase a PASS on. Record `docs/2026-09-13_work-item-11.5_stock-scale-aggregation-closure.md`, manifests `outputs_step11/c2_uk/step11_11-5_uk_reseed.json` and `c2_it/step11_11-5_it_reseed.json` | 11.3, 11.4 | no |
| **11.7** | 🔴 **WITHDRAWN, and NOT revived at closure (2026-09-13).** Offered, then withdrawn the same session on the model's own judgement with no author objection — `Prompts/RESUME.md` §6, *“OPTION (c) — ITEM 11.7 — WAS OFFERED AND THEN WITHDRAWN”*. It is **a rendering, never a result**, so it adds no evidence to the board, and its re-pointed `D-EU-88` district-viewer input still does not exist. If it is ever revived, **every inherited bar below applies unchanged**. The original scope is kept verbatim: ⚪ **3D stock visualisation, ONE static self-contained `.html`** — added 2026-08-28 at the author's request. Renders the Step 11 stock aggregate on the **existing** OpenUBEM 3D export `OpenUBEM/docs/docs_ACTIVE/europeanLocations/outputs_3D`, in the vocabulary and conventions of `OpenUBEM/docs/docs_EXPLANATION/OpenUBEM_fundamentals.md`. 🔴 **It is a rendering, never a result, and it inherits every bar**: Arm D and Arm F **never share a colour scale or a legend** (`G10.9`); every Arm F surface is labelled a **LOWER BOUND** with **no magnitude attached** (`G10.22`); **no per-dwelling value is rendered at any zoom** (`G11.13`); every figure is **HEATING-ONLY** and stated **relative to its own control** (`G10.12`); the **Lyon geometry provenance** is printed on the page (`G10.11`). ⚪ **Read-only on the OpenUBEM tree** — it reads the export and never writes into it. No new simulation, no new artefact in their tree. 🟡 **Added 2026-09-03 (`D-IMP-1`, I-8):** input re-pointed to the `D-EU-88` district-viewer output once it exists — **geometry only, no EUI rendered on the page**; `G11.13`'s no-per-dwelling-value rule stays exactly as above. `D-EU-88` has not started; nothing built here today | 11.5 | no |
| **11.6** | 🟢 **DONE 2026-09-13. Gate board, mutation battery, dossier** — all 18 declared `G11.x` scored (`V11.g` SUITE COMPLETE): 14 PASS / **`G11.6` FAIL** / **`G11.12` FAIL** / `G11.7` INFO (permanent) / `G11.4` NOT CHECKED (offline). New tool `tools/4thJ_step11_stockboard.py` (imports 11.3's trigger loop, never re-implements) fed the three gates with no earlier stock-scale data — full populations, no `--limit`: London 7,602 flats, Bologna 29,902 flats. **`G11.8` and `G11.18` both PASS real** (DHW category mix within 3 pp of Table 1; stock mean DHW 202.41/200.35 l/dwelling/day against 200 ± 10 %). **`G11.6` FAILS for the SAME mechanism `G11.12` already found**: laundry appliances SATURATED and three appliances 74–84 % below CREST's published cycle count, both folds — consistent with `G9.6`'s own Step 9 FAIL, band never moved. `tools/4thJ_step11_selftest.py` extended with two new registered mutations (`g11_8_reshape_dhw_mix`, `g11_18_triple_dhw_volume`, both against a scratch copy of the REAL `it`-fold stockboard output) — **battery 18 HIT / 0 MISS / 1 already-failing (`G11.6`), COVERAGE CLAUSE PASS**. Record `docs/2026-09-13_work-item-11.6_gate-board-battery-closure.md`, evidence `outputs_step11/g11_6_18/` | 11.5 | no |

⚪ **No Speed job and no GPU.** Step 9 ran entirely locally, and Step 11's addition is population size, not
model size. If that stops being true, it is recorded before the first submission, not after.

---

## 5. WHAT THIS STEP CANNOT DELIVER

* **No per-dwelling prediction**, at any scale (`G11.13`). Scale raises confidence in the *aggregate*; it
  does nothing for the individual household, and `9C` says why.
* **No claim that Step 9's FAILs were a small-sample artefact** unless 11.2 diagnoses `G9.7` and the
  diagnosis is independent of the re-measurement.
* **No cross-population R² comparison** without the declaration `G11.16` requires (§1.2).
* **No end-use that also appears in Step 10's reconstruction** (§3).
* **No Arm F aggregate presented as an estimate** — it is a lower bound, labelled as one (§2.1, `G11.17`), and **no numeric bias magnitude is attached to it**.
* **No validated mapping row without its validation scale** — `G9.2`'s clause is inherited verbatim: a row
  labelled VALIDATED with no scale is a **FAIL**, not a warning.

---

## PROGRESS LOG

### 2026-08-26 — planned

Authored alongside Step 10 after the author fixed the scope: Steps 8 and 9 are preserved as a closed
chapter and the OpenUBEM integration becomes Steps 10 and 11 **inside paper 4**.

The design point that shaped this document: **Step 9's `G9.12` was scored on 100 dwellings per fold, which
is exactly the registered `≥ 100` floor.** The gate was evaluated at its weakest admissible population,
and Step 11 is the first configuration in this project that reaches the 100–500-dwelling range the source
models were actually validated in. That is a real change in what the gate can tell us — and §1.2 records
the price, which is that the two populations are not comparable without saying so.

### 2026-08-26 (evening) — one consequence carried from `RL29`

Step 11's exposure to this round is small and it is worth saying why: `RL28` and `RL29` were about
**peak diversity** and **geometry**, and Step 11 is about an **activity-to-load mapping** that neither
touches. One thing did cross — the Arm D / Arm F separation is a **directional bias**, not noise, so an
Arm F aggregate is a lower bound rather than an estimate (§2.1, `G11.17`). The magnitude was refused: it
rests on a citation whose own CrossRef line returns a different paper.

🔴 **`G9.7`'s 2–4× DHW magnitude error is untouched by this round.** No DHW deep-research round was
commissioned, deliberately — `RL25` §B10 already carries Jordan & Vajen's figures, and work item 11.2
vets our registered band against the source table rather than against a new dossier.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No Step 9 threshold moved and no `G9.x`
gate ID reused — Step 11 opens a `G11.x` series and states its inheritance per gate.

### 2026-08-27 — 🟢 WORK ITEM 11.2 IS DONE, AND `G9.7`'s FAILURE HAS A MECHANISM

Record: `docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`. Findings `163`–`166`, decision
`D-S11-1`, summarised in §1.3a. **Nothing was re-run**: four read-only checks over the shipped
`outputs_step9/` tree and the vendored `jordan_vajen_iea_task26_v2.0_2001.pdf`
(md5 `c7c460924ef66588649b2473b706e2b9`).

🔴 **The 2–4× is not in the DHW model. The model is a cell-for-cell transcription of its table**
(1 / 6 / 140 / 40 L per load; 28 / 72 / 20 / 80 L per day; portions 0.14 / 0.36 / 0.10 / 0.40;
total **200.02**). **The band and the volumes come from two different papers**, and the ratio between
their bases is exactly `n_members`.

🔴 **The 2026-08-26 (evening) entry above is corrected by this one.** It says *"`RL25` §B10 already
carries Jordan & Vajen's figures, and work item 11.2 vets our registered band against the source
table"*. The band **is not in the source table and never was** — vetting it there could only ever
return "absent", which is what `FINDING 138` already returned. What the band needed was its
provenance traced forward from `RL13`, not its value looked up in Jordan & Vajen. 🔴 **The general
lesson, and it is not specific to DHW: a value's SOURCE is a claim that has to be checked
separately from the value.** `FINDING 138` opened the right report and asked the wrong one.

⚪ **11.2 was picked up because it needed no GPU, no Speed job and no OpenUBEM cell** — it was the
one item in Steps 10 and 11 that could be closed while `1287613` was still running.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No band moved, no checker edited, no
`G9.x` verdict changed: `G9.7` still **FAILS 300** at 100.16 / 117.65 / 91.06 against 30–50.


---

### 2026-08-27 (later) — THE RULING CAME BACK THE SAME DAY, AND EXECUTING IT COST A GATE

🟢 **`D-S11-1` ruled (d)(ii) → (b) by the author**, recorded in §8 of
`docs/2026-08-27_work-item-11.2_G9.7-diagnosis.md`; `D-S9-2` item 7 is ruled with it. `G9.7` and
`G11.7` are permanent `INFO` on the `G8.7` precedent, the 30-50 band is left exactly as registered,
the deviation is reported in full, and Fuentes et al. (2018) is finally in a citation table. What
was executed is §9 of that record; Step 9's own log carries the same entry from its side.

🔴 **The part worth remembering is not the ruling, it is the price.** Reclassifying a
gate to `INFO` is not free even when it is right: `G9.7` was the **only** detector of
`scale_dhw_by_2` in the Step 9 battery, and `4thJ_step9_selftest.py` had already declared `G9.8`
blind to it. An `INFO` gate cannot fail, so the mutation now passes unremarked — demonstrated by
doubling every `dhw_*` column and watching the gate return `INFO` at medians
`200.31 / 235.30 / 182.13`. **A gate carries two jobs — it scores a quantity and it detects a
mutation — and a decision that correctly retires the first silently retires the second.** That is
`D-S11-2`, and it is the author's to close because the fix is a new scored arm.

🟢 **CLOSED THE SAME DAY.** The author ruled the arm: per dwelling, at Jordan & Vajen's own
**200 l/day, +/-10 %**. It is `G9.15` in `4thJ_gates_step9.py`, it takes `scale_dhw_by_2` over
in the registered table, and it was seen failing before it was trusted - shipped `PASS` at
200.79 / 201.01 / 199.47, doubled draws `FAIL` at 401.58 / 402.03 / 398.93. `G11.18` is declared
in `4thJ_11_stockEndUseLoads_val.md` and inherits it unchanged. ⚪ **A scale / regression
arm, not an external validation** - 200 l/day is the emitter's own input - and the medians are
printed on every run because a median arm at the same tolerance would fail two folds. 🔴 **No
band moved: `G9.7` and `G11.7` are still `INFO` and 30-50 is still 30-50.**

🟢 **And the citation repair paid for itself in one run.** `FUENTES-2018` was added
from `RL13`'s metadata; `G9.4` returned `FAIL` on the first online invocation because `RL13`'s
`81(1)` carries an issue number the publisher's record does not have (`FINDING 167`). ⚪ **A Tier 2
row was wrong in a checkable field, and the check that caught it is one this project already
owned** — which is the argument for adding the row rather than citing the band loosely in prose.


---

### 2026-08-27 (last, later) 🟢 - WORK ITEM 11.1 IS DONE

🟢 **Four gates scored, and they are the only four Step 11 has.** `G11.1`-`G11.4`,
online `PASS 61 / PASS 192 / PASS 149 / PASS 4`. The remaining fourteen are printed **`NOT RUN` by
name** and the runner prints **no tally at all**: `V11.g` says the declared suite is the scored
suite, and a partial run that prints a tally reads as a complete one.

🔴 **`FINDING 168`: `G11.15` was declared twice** - section D's pre-registered
double-count gate and, since `D-S11-2` the previous evening, the DHW per-dwelling arm. `V11.g`
compares SETS and a set does not count a duplicate twice, so the coverage clause would have gone
green with one of the two gates permanently unscored. The newcomer moved to **`G11.18`**; nothing
had been scored under either ID. ⚪ **The detector outlives the repair:** the runner
censuses gate-table row heads and REFUSES to score an ambiguous document, and `duplicate_gate_id`
is a registered case in `tools/4thJ_step11_selftest.py`.

⚪ **Why this is not a tautology, since section 2 says the mapping is NOT
re-authored.** The audit asserts three things it could find false: the rows are the same rows
(md5s printed on every run), the bars are the same bars (parsed out of the validation document's
INHERITANCE COLUMN, never from a constant in the runner), and the code is the same code
(`g9_1`-`g9_4` are imported from `4thJ_gates_step9.py`, not re-implemented - a second opinion is
not an inheritance). The battery's `drop_rows_to_20` case is the proof: twenty well-formed rows
leave every gate's own verdict at `PASS`, and the audit FAILS anyway, on the inherited count.

⚪ No band, threshold or tolerance moved. No Step 9 artefact was edited or
regenerated. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.

---

### 2026-08-27 (night, last) — `D-S11-1` DIRECTIVE 2 IS DISCHARGED: THE PASSAGES ARE DRAFTED

🟢 **Directive 2 of the `D-S11-1` §8 ruling — *"in the manuscript methods and limitations, explain
that Jordan & Vajen (2001) specifies 200 L/dwelling-day … yielding ~100 L/person-day for typical
2-person European households"* — is no longer an outstanding obligation.** The text is drafted at
`writing/4thJ_writeup_notes.md` §7 (`7.1` Methods, `7.2` Results, `7.3` Limitations (a)–(e),
`7.4` caption rule, `7.5` what it does not do). The notes file goes 230 → 375 lines; backup
`4thJ_writeup_notes.md.bak_pre_ds111_dir2`, `[ -s ]`-verified before the append.

🔴 **What the wording carries beyond the directive's own sentence**, because four later findings
attached themselves to the same paragraph set: §3's **heating-only rule** (the pooled 66.8677, the
min/median/max and the FR/ES split may not appear without those words), §3.1's **two-end-use fact**
(93.768 is the model's total, not a building's — `Lights`/`ElectricEquipment`/`WaterUse*`/`People`/
cooling coils all absent, so no TABULA, national-EUI or stock projection is reachable), §5's **`26`**
(26 dwellings in 12 buildings, below the 30-per-fold minimum, the same shape as `H10`'s 9 / 5 / 3),
the **`f = 0` flat-electricity constraint** (381 series, every value exactly 3, so a null there is an
artefact of the input), and the **single-fold caveat on both Leg-5 comparison arms** (1.568 vs 1.508
vs 1.539 against the `es` noise floor 0.529 — verdicts comparable, band values not; truncation
measured on the Qwen arm only).

🔴 **Two things the passages deliberately keep and would be easy to lose.** (i) `G9.7`'s **verdict is
withdrawn but its deviation is reported in full** — 100.16 / 117.65 / 91.06 against 30–50 — because a
verdict asserts comparability and the medians assert only what was emitted. (ii) The limitation names
**what the classification cost**: `G9.7` was the only detector of a DHW scale mutation, and `G11.18`
exists to replace the detector, not the verdict.

🔴 **Fuentes et al. (2018) is still unread.** §7.1 flags the 30–50 L/person-day at 60 °C as
**bibliographically verified and substantively unverified** (`FINDING 47`, `FINDING 167`), and the
manuscript may not imply the second from the first. That flag is the one thing in §7 that a person
can retire, and only by reading the paper.

⚪ **Nothing moved.** No band, threshold, verdict or count changed; no gate was scored; no code ran;
no Step 9, 10 or 11 artefact was regenerated. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`
untouched. ⚪ **No manuscript file was created** — §7 is drafted passages inside the notes, and the
manuscript itself remains unwritten.

### 2026-09-03 — no-core review, `D-IMP-1` (I-8): Arm F redefined, item 11.7 re-pointed

`D-IMP-1` ruled (a). Two dated amendments, both additive, nothing built: §2.1 — Arm F is redefined
for the no-core regime as check-FAIL-or-unusable-footprint → one box per floor (no longer a
convexity refusal alone); `G11.17`'s LOWER BOUND / never-pooled rule is unchanged. Item 11.7 —
input re-pointed to the `D-EU-88` district-viewer output once it exists (geometry only, no EUI on
the page); `G11.13` stays. Mirrored one line in `_val.md`'s `G11.17` row. `D-EU-88` has not
started; Step 11 does not re-open.

---

### 2026-09-08 (last+46), same day — 🟢 **WORK ITEM 11.3'S RUNNER EXISTS**; 🔴 **the stock population has 100 diaries, not 1,200**; 🟢 **London 706 installed and verified after two defects were caught**

Record: `Step11_docs/docs/2026-09-08_work-item-11.3_trigger-campaign-runner-built.md`. Author's
instruction: *"ok once you got the data continue to build step11 lets go"*. **Nothing scored, no
`G11.x` verdict computed, no EnergyPlus cell simulated, no compute.**

🔴 **THE INSTRUCTION'S CONDITION WAS MIS-SPECIFIED AND SAYING SO IS PART OF THE ANSWER.** The London
export widens the `C2` **population**; it does not unblock **Step 11**. Item 11.3 depends on Step 10
items **10.4 and 10.6** — a *simulated* `C2` cell and its manifest — and **no `C2` cell has been
simulated**, because `D-EU-55` authorises Bologna only. What was genuinely unblocked is the runner,
and that is what was built.

🟢 **`tools/4thJ_step11_trigger_campaign.py`.** For every drawn flat in every `C2` Arm D cell it runs
the Step 9 trigger on **that flat's own diary**. **Three things imported, never re-implemented** —
the state machine (`simulate_dwelling`), the dwellings (`build_dwellings`, which refuses unless it
reproduces Step 8's shipped schedules), and the flat→diary binding (read from the `C2` manifests'
own `schedules[]`). ⚪ *A re-implementation is a second opinion, and a second opinion is not an
inheritance.*

🟢 **A REFACTOR OF A CLOSED STEP, PROVEN INERT.** `simulate_dwelling` did not exist — the loop was
inline in `run_fold`. Extracted verbatim; `rng` became a parameter defaulting to the same
`"s9|<seed>|<hid>"` stream. 🔴 **Verified, not asserted: Step 9 fold `it` run end to end before and
after, and the md5 of EVERY emitted artefact is identical, stdout included.** Backup
`tools/4thJ_step9_trigger.py.bak_s11_extract`. ⚪ **A refactor is not a re-score** — no verdict
recomputed, no band moved, 11.1's carry-over audit untouched.

🔴 **THE `G11.15` SEAM NOW HAS A MEASURED BASIS.** Read out of
`openubem/semantic/european_schedules.py`: `build_step8_gain_series` conserves the annual mean at
exactly `BASE_GAIN_W_M2` for every `f` **and asserts its own conservation**, and attaches ONE
`OTHEREQUIPMENT` at `Watts/Area = 1.0`. **So `C2` carries one LUMPED internal gain — occupants,
appliances, lighting together — as its INPUT and produces SPACE HEATING as its result; `f`
redistributes it in time and never rescales it.** Paths: **Step 10 = `space_heating`; Step 11 =
`appliance_electricity`, `dhw`.** 🔴 **Step 11's appliance electricity must NEVER be injected back
into a Step 10 heating model — that heat is already inside the conserved gain, and adding it again
is the double count.** ⚪ **Consequence: a flat's appliance MAGNITUDE has no path into its heating
number at all; only the TIMING crosses the seam.** Any sentence implying otherwise is false.

🔴 **THE FINDING THAT NARROWS §1.1: ONE HUNDRED DIARIES, NOT ONE THOUSAND.**
`4thJ_step10_assign.step7_index()` indexes **exactly 100 presence schedules per fold** — all Step 7
shipped. Step 9 seeds its per-dwelling RNG `"s9|<seed>|<hid>"` and draws ownership per `hid`, so
**two flats that drew the same household have IDENTICAL loads**. Seen: 170 flats over **6** buildings
already bind **59** of the 100. **The stock population has thousands of BUILDINGS and at most 100
DISTINCT OCCUPANCY DIARIES per fold, and on this Step 7 emission it cannot have more.** ⚪ §1.1's
claim is not wrong, it is **narrower than it reads**: Step 11 is the first configuration with that
many buildings and one shared weather file, **not** the first with that many occupants. **An R²
improvement at stock scale would be evidence about spatial and geometric aggregation, never about
occupant diversity** — claiming otherwise is the comparison `G11.16` calls a FAIL.

🔴 **`--diary-diversity` HAS NO DEFAULT AND THE RUN REFUSES WITHOUT IT (`S9`).** `replicate` = one run
per household (100/fold, ~2 min) replicated onto flats; `reseed` = one run per flat, ownership
redrawn (~1.2 s/flat → Bologna Case B alone ≈ **9 h**, `sbatch` work), **occupant diversity still
100**. **A default would have silently decided what a stock number means.** ⚪ A third option —
widening the Step 7 pool — is **named, not done**: it re-opens two closed steps and breaks
`build_dwellings`'s reproduction guard.

🟢 **TEN REFUSALS `S1`–`S10`, EVERY ONE SEEN FAILING WITH A PASSING CONTROL**, on a fixture of
`C2`-shaped manifests over 6 real Bologna buildings (60 cells, 170 flats) whose **assignment is
real**: `S1` France · `S2` Arm F/pooling · `S3` no cells (missing dir AND empty dir) · `S4` a
manifest `G10N.14` would fail, an incomplete cell, an unrotated cell · `S5` `G11.14` absent column
and `act2` re-admitted · `S6` a diary changed since the `C2` run · `S7` `--scored` · `S8` a `C1`
result, and cells spanning two folds · `S9` the unset flag · `S10` an end-use on both paths and one
on neither. **Nothing was written into `Step11_docs/outputs_step11/`.**

#### The London 706 — installed and verified, after two defects caught by re-measuring

🔴 **DEFECT 1, PATH:** the 706 first landed only at `openubem/outputs/eu_evidence/EU-11/
GB-LDN-STDUNSTANS_final_2026-09-07/layouts` while the canonical path and the docs mirror still held
the old 451 — so a campaign reading "the district's layouts directory" would have taken the new
Bologna and the old London **silently**. Reported; they installed it at the canonical path.
🔴 **DEFECT 2, AND IT IS THE SHARPER ONE: they preserved the old 451 as `way_pre_D-EU-113_backup_
2026-09-08/` INSIDE `layouts/`.** Our mandatory recursive walk then returned **1,157 = 706 + 451** —
a clean-looking, plausible, completely wrong population mixing two emissions of one district, with
no error raised (`eligible=1124`). ⚪ **The nesting rule that protects us became the thing that
betrayed us**: `relation/`+`way/` force a recursive read, and a sibling of old payloads turns correct
behaviour into the wrong answer. Reported; **moved out to `layouts_pre_D-EU-113_backup_2026-09-08/`,
a sibling of `layouts/`, not a child.**

🟢 **RE-MEASURED OURSELVES AFTER THE FIX** (`find -name '*.json'`, never `ls`, never their counts):
**Madrid 1,175 · London 706 · Bologna 1,211 · Lyon 297**, docs mirror agreeing on all three.
London preflight: **706 checked / 685 eligible / 9 Arm F / 12 FAILED**, audit false on 53, worst
`9.960e-05`.

🔴 **THE 12 FAILS ARE REAL AND SIX ARE REGRESSIONS** — six buildings that were `IMPUTED_COUNT` in our
frozen 451 are now `INTERZONE_MISMATCH_REROUTED`, plus five Arm F and one new. Their director accepts
them as-is. ⚪ **That settles it on their side and not on ours: whether a payload that COSTS SIX
ELIGIBLE BUILDINGS replaces the population we froze is our author's re-pre-registration to sign.**
Also **not additive** — all 451 files changed bytes and 5 layouts genuinely moved (`uk` zone total
1,728 → 1,813).

🟢 **`FINDING 258` IS DIAGNOSED AT LAST.** The new payload carries `failures`, `gap_area_m2`,
`overlap_area_m2`, `outside_area_m2` on 697 of 706. 53 audit failures: 32 `(AREA_GAP, AREA_OVERLAP,
OUTSIDE_FOOTPRINT)`, 18 `(AREA_GAP, OUTSIDE_FOOTPRINT)`, 2 `(AREA_GAP,)`, 1 `(OUTSIDE_FOOTPRINT,)`;
gap max `1.9184e-02` m², overlap max `7.155e-03` m², outside max `1.7534e-02` m². **Four to five
orders of magnitude over the `footprint × 1e-9` topology tolerance while `area_error_fraction` clears
the 0.01 conservation bar by ~100×. The correction we made to our OWN record is now confirmed by
data, not by argument: it is a TOPOLOGY GAP and `area_error_fraction` was never the quantity that
failed.** 🔴 Decision unchanged — **reported, never gated**; the frozen prereg still says "rounding
residue" and the next re-pre-registration must carry the correction, now citing measured areas.

⚪ **OWED, ALL THE AUTHOR'S: (1) `--diary-diversity`; (2) a second `D-EU-55` sentence for Madrid or
London; (3) does the 706 replace the frozen 451 at the cost of six buildings; (4) run the Bologna
shakedown, which 11.3–11.7 all wait on.** **Step 11 is still NOT RUN; 11.4–11.7 remain PLANNED.**

---

### 2026-09-08 (last+47), same day — 🔴 **THE `C2` RUNNER HAD NEVER BUILT AN IDF**; 🟢 **three harness defects found by a four-cell smoke**; 🟢 **`RE-PRE-REGISTRATION 2` adopts the London 706**; 🟢 **the Bologna shakedown is RUNNING at full size**; 🟢 **`--diary-diversity` ruled `reseed`**

Record: `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md` §9. Author's sentence:
*"continue as you recommend lets go use bigger datasets"*. **Nothing scored, no `G10N.x` or `G11.x`
verdict computed.**

🔴 **THE SENTENCE IS READ AS TWO RULINGS AND WRITTEN DOWN SO IT CAN BE CORRECTED IN ONE LINE.**
(1) adopt the London 706; (2) run the authorised district at FULL SIZE, not a token subset.
🔴 **NOT read as a third:** it names no district and does not mention EnergyPlus, so **`D-EU-55` is
NOT widened** — and `R2` was **observed refusing Madrid and London after the sentence was given**.

🔴 **THE RUNNER SHIPPED LAST SESSION WITH TEN REFUSALS SEEN FIRING AND HAD NEVER PRODUCED ONE IDF.**
Three defects, all ours, none physics: **(1)** `KeyError: 'shadow_method'` — upstream's header
template carries a `ShadowCalculation` block and we supplied 5 of 8 fields; the three constants are
now **imported**, never typed. **(2)** `HVACTemplate:* objects ... not supported directly`, fatal in
0.06 s — the binary needs **`-x`**. **(3)** 🔴 **3 of 4 cells died on `readvars.audit ... used by
another process`**: `-r` writes it into the PROCESS working directory, not `-d`, so parallel workers
destroyed each other's file. Fixed with **`cwd=run_dir` + `-d .`**, upstream's own invocation.
⚪ **Defect 3 is the dangerous one — it looks like scattered physics failures, varies with worker
count, and would have salted a 10,360-cell campaign with false `ENERGYPLUS_FAILED` cells no
downstream gate could tell from real ones. All three were found by running FOUR cells before
launching ten thousand.**

🟢 **16 of 16 cells then completed** (91 s, 16 workers). Building `27410`, 16 zones, 3,754.5 m²:
**case A `cf` = 1.0000, case B `cf` = 0.9681**, EUI 49.37 / 49.40 kWh/m². ⚪ The synchronised control
behaves as a control and the independent case diversifies — **a harness observation on two
buildings, NOT a result.**

🟢 **`RE-PRE-REGISTRATION 2`** (473 → 596 lines, append-only, backup
`impl/prereg_step10_nocore_DRAFT.bak_20260908_pre_rr2`): frozen md5
**`1bc21094…` → `055331f285426a9928ca8f124fab7cc3`**. Population **re-measured by us**:
**es 1,100 / 11,244 · uk 685 / 2,316 · it 1,036 / 13,792 → 2,821 buildings, 27,352 Arm D zones**
(was 26,764; `uk` was 439 / 1,728). ⚪ **The trade is recorded both ways: +246 eligible buildings and
+588 zones, at the price of SIX that used to be eligible and are now rerouted.** All twelve London
FAILs stay FAIL. 🔴 **`R1` seen failing by name against the restored pre-RR2 text; live file
re-verified `OK`.**

🟢 **THE SHAKEDOWN IS RUNNING:** `--district IT-BOL-GALVANI2 --shakedown --workers 16 --limit 0`,
**10,360 cells**, detached, ~16 h, log `_local_runs/step10_nocore_bologna_20260908.log`, preflight
report carrying the **RR2** md5. 🔴 **An earlier launch was killed three minutes in on purpose** — it
had passed preflight under the superseded md5, so every manifest would have cited a superseded
pre-registration.

🟢 **`--diary-diversity` RULED `reseed`** — one run per drawn flat, ownership redrawn, so no two flats
carry a byte-identical series; `replicate` is the smaller dataset the sentence declines. 🔴 **It does
NOT widen the occupancy pool: presence still comes from the 100 diaries Step 7 shipped, and `reseed`
varies OWNERSHIP and the draw, never who lives there.** The flag still has **no default**, and a
contradicting value is refused **by name** (`S9b`) — both seen firing, `reseed` passing as control.

⚪ **OWED, NOW ONLY TWO, BOTH THE AUTHOR'S: (1) a second `D-EU-55` sentence naming Madrid and/or
London; (2) whether the finished shakedown may be READ as a scored `G10N.x` result (`R8` refuses
`--scored` until then).** **Step 11 items 11.4–11.7 stay PLANNED until the shakedown's cells exist.**

---

### 2026-09-08 (last+48), late the same day — Step 11 is UNBLOCKED IN PRINCIPLE AND STILL NOT RUN

Record: `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md` §10. **No Step 11 run,
no `G11.x` verdict, no cell simulated by this step.**

🟢 **What changed upstream of Step 11.** The author's own words widened `D-EU-55` — *"finish all
three cities"*, *"all neighbourhoods done you can go until the end"*, *"use 32 cpu of all speed
reserouces"* — and **two `C2` campaigns are now running on Speed at 32 cpu each**: Madrid (11,000
cells) and Bologna (10,360). Items **11.4–11.7 depend on Step 10's items 10.4 and 10.6**, a simulated
`C2` cell and its manifest, and those cells are being written now rather than being waited on.

🔴 **London contributes NOTHING to Step 11 for the time being, and the reason is not permission.**
`R5` refuses the district outright: 12 of its 706 payloads are `INTERZONE_MISMATCH_REROUTED` and **a
partial population is not a campaign**. The `uk` fold therefore has **no `C2` manifests to bind
diaries to**, so any Step 11 result covering all three folds is blocked on OpenUBEM re-emitting those
12 — not on us and not on the author.

🔴 **THE 100-DIARY CEILING IS UNCHANGED BY ANY OF THIS.** `--diary-diversity` stays ruled `reseed`
(no default, `S9`/`S9b` still refuse), and `reseed` varies **ownership and the draw**, never who
lives there. Step 7 shipped **100 presence schedules per fold** and that is still the whole pool.
⚪ **An R² gain at stock scale is evidence about geometry and aggregation, never about occupant
diversity** — and now that the stock is about to double in size, that sentence gets easier to
forget and more expensive to get wrong.

🔴 **The `G11.15` seam is unchanged too.** Step 10 = `space_heating` from ONE lumped internal gain
whose annual mean is conserved; Step 11 = `appliance_electricity` + `dhw`. **Only TIMING crosses the
seam, never magnitude**, and Step 11's electricity is never injected back into a Step 10 heating
model.

⚪ **Also unchanged: nothing here is scored.** The `C2` cells Step 11 will read are authorised to
exist and **not** authorised to be read as a `G10N.x` result — `R8` still refuses `--scored`, and
that single sentence from the author is the one item owed. **11.4–11.7 stay PLANNED.**

---

### 2026-09-08 (last+49), after midnight — 🔴 **STEP 11 STAYS PLANNED: THE STEP 10 CAMPAIGNS WERE STOPPED AND THERE ARE NO CELLS**

Record: `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md` §11 and
`Step10_docs/prereg_step10_nocore_DRAFT.md` `RE-PRE-REGISTRATION 4`.

🔴 **Nothing in this entry changes the seam and nothing changes Step 11's design.** It records why
Step 11 has no input yet.

🔴 **DEFECT 8, found by the Madrid campaign in its first eighty cells of eleven thousand:** the
no-core layout emitter names **every storey `F0_dwelling_0`** when a building has one dwelling per
floor, so **geometrically distinct flats are emitted under ONE identity** — `relation/12638102` has
five flats and one name. **Measured: 233 of 1,100 eligible Madrid buildings (21.2%), 35 of 1,036
Bologna (3.4%).** `zone_count_emitted` — what the gates read — counts flats that cannot be told
apart, so the population is not the one on record. **`R7` had a blind spot that let it through**
(it compared distinct-slug count against `set(names)`, which collapses the duplicate on both sides);
`R7` is **tightened a third time**, seen failing on both populations and passing on a control.
**All three runs were stopped**; prereg md5 `7ce1c041…` → `e1f2822a…`.

🔴 **WHAT THIS MEANS FOR STEP 11, PRECISELY.** Step 11 consumes **finished Step 10 cells**, and there
are none — the 22 Madrid manifests written before the stop are **evidence, never cells to be read**.
**Items 11.4–11.7 stay PLANNED**, unchanged, and they do not move until the author rules on whether
the affected buildings are EXCLUDED or FATAL, because that ruling changes the **population** Step 11
would draw its stock from.

⚪ **The seam is untouched** (`G11.15`): Step 10 is space heating from one lumped internal gain whose
annual mean is conserved; Step 11 is appliance electricity and DHW; only TIMING crosses, never
magnitude. **Nothing in defect 8 touches the gain, the diary pool, or the `--diary-diversity`
ruling** (`reseed`, still no default, still refused by name by `S9b` on a contradicting value).

⚪ **A Step 11 lesson taken from a Step 10 defect, and worth writing down before 11.4 is built:** the
Step 10 runner writes **no manifest for a failing cell** and aggregates every diagnosis only after
the last cell returns, so a cancelled run loses all of it. **Step 11's own campaign must not repeat
that** — a failure's record belongs on disk when it happens.

---

### 2026-09-13 (last+264) — 🟢 **STEP 11 IS CLOSED. THIS ENTRY BACKFILLS last+229–last+263, WHICH THIS LOG NEVER RECORDED**

🔴 **Read the gap first, because it is the lesson.** Between the entry above (last+49,
2026-09-08, *“STEP 11 STAYS PLANNED”*) and today, the whole step was built, run, scored and closed —
and **not one line of it was written here.** The state lived in the `docs/` closure records, in the
§4 work-item table, and in `Prompts/RESUME.md`. A reader who trusted this Progress Log would have
concluded the step was never started. The three-artefact ritual asks for all three artefacts every
time; two of three is how a log stops being merely incomplete and becomes misleading. ⚪ **Nothing
below is new measurement** — every number is re-read from the artefact named beside it, never
restated from a summary sentence.

**11.3 — the campaign (built last+46, run last+236).** `tools/4thJ_step11_trigger_campaign.py`,
`--diary-diversity reseed`, no `--limit`, zero refusals, zero errors. Bologna **29,902 flats over
1,126 buildings**, 6,126.2 s; London **7,602 flats over 1,200 buildings**, 1,537.3 s. Both manifests
carry `n_flats_enumerated == n_flats_run` and `smoke_run: false`. **The exclusion ruled mid-launch:**
42 Bologna + 7 London buildings hold synthetic floor-averaged diaries rather than real per-flat Step 7
diaries; the per-flat check refused them and the author chose EXCLUDE, so **49 buildings are declared
absent, not zero**. Filtered copies of `cells/` were used — 420 IT and 70 UK cells dropped, skip counts
matching the exclusion lists exactly — and **Step 10's own output was never touched**. The tool scores
nothing, by design.

**11.4 — the accounting path (2026-09-13).** Closed **on 11.3's own construction, not on new work**:
`STEP10_END_USES`/`STEP11_END_USES` are a fixed disjoint partition, `check_seam` (`S10`) refuses any
overlap or unknown end-use before a manifest is written (seen refusing on a planted overlap), and
`population_declaration()`'s `accounting_paths` field is present byte-identical in both cities' real
output. The 49 excluded buildings are on **neither** path — declared absent, which is not a seam
violation. Record `docs/2026-09-13_work-item-11.4_accounting-path-closure.md`.

**11.5 — stock-scale aggregation (2026-09-13).** `tools/4thJ_step11_aggregate.py` **imports** 11.3's
trigger loop and `G9.12`'s own scorer and re-implements neither — a re-implementation is a second
opinion, and a second opinion is not an inheritance. A 2,000-flat Bologna smoke ran first and was
flagged a smoke, not carried forward. Full populations then ran: **`G11.12` FAIL, R² = 0.4347 (`uk`,
7,602 flats) and 0.0781 (`it`, 29,902 flats)**. ⚪ `G9.12` had already FAILED the same band at n=100 in
Step 9; **two much larger, independently drawn populations failing the same way is evidence the
measurement is real**, and nothing was adjusted to chase a PASS. Record
`docs/2026-09-13_work-item-11.5_stock-scale-aggregation-closure.md`.

**The `G11.12` investigation (last+262, run by the author in a separate session).** `FINDING`s
`270`–`274`, report `docs/2026-09-13_G11.12-stock-scale-failure-investigation.md`. 🔴 **An earlier
in-file draft (`FINDING`s `168`–`172`) had a sign error** — it read the best circular-shift R²
(0.60–0.69) as if timing nearly explained the failure, but that peak sits on the **anti-correlation
branch** (r < 0); on the real positive branch, shifting gains almost nothing in `uk` and caps at
R² = 0.27 in `it`. Only `270`–`274` stand. **Root mechanism (`FINDING 272`): CREST's reference profile
is >77 % laundry at 11:00, and this model suppresses laundry starts 80–90 % under `D-S9-1`** — only
primary HETUS activities trigger appliances, and laundry is recorded as a secondary activity.
Occupancy drift is a Step-9-manifest artefact, not a population difference (`FINDING 273`); the
scoring arithmetic re-verified clean, zero bugs (`FINDING 274`).

**The ruling on `G11.12`: KEEP FAIL, no code change.** `D-S11-1`'s own INFO-reclassification criterion
is a **basis/denominator mismatch** — a per-person band scored against a per-dwelling model — and that
is not what is happening here. `G11.12` measures a real shape correlation that **could** pass if the
shape matched, so reclassifying it `INFO` would silently retire its mutation-battery coverage for no
matching reason.

**11.6 — board, battery, dossier (2026-09-13).** `tools/4thJ_step11_stockboard.py` (again importing
11.3's loop, never re-implementing it) fed the three gates that had no stock-scale data; both full
populations ran clean in the background, no `--limit`. `tools/4thJ_gates_step11.py` then scored **all
18 declared gates, SUITE COMPLETE** (`V11.g`): `{"PASS": 14, "FAIL": 2, "INFO": 1, "NOT CHECKED": 1}`.
🟢 **`G11.8` PASS real** — DHW four-event mix within 3 pp of Table 1 in both folds.
🟢 **`G11.18` PASS real** — stock mean DHW **202.41** (`uk`) / **200.35** (`it`) l/dwelling/day
against 200 ± 10 %.
🔴 **`G11.6` FAIL real** — three appliances (`tv_2`, `vcr_dvd`, `tv_receiver_box`) 74–84 % below
CREST's published cycle count and the laundry appliances SATURATED, **both folds**. 🔴 **This is
`G11.12`'s mechanism, not a second defect** — the same `D-S9-1`, and consistent with `G9.6`'s own Step 9
FAIL, where the band never moved either. `G11.7` stays permanent `INFO`; `G11.4` is `NOT CHECKED`
offline. Because `G11.8`/`G11.18` are genuine new PASSes they earned detectors:
`tools/4thJ_step11_selftest.py` gained `g11_8_reshape_dhw_mix` and `g11_18_triple_dhw_volume`, both
built the existing G11.9/10/16/17 way — a scratch copy of the **real** `it`-fold stockboard output,
mutated in place, never invented from nothing. **Battery 18 HIT / 0 MISS / 1 already-failing**
(`G11.6`, `ALREADY_FAILING_AT_BASELINE`, `V11.b`), **COVERAGE CLAUSE PASS**. Record
`docs/2026-09-13_work-item-11.6_gate-board-battery-closure.md`; evidence
`outputs_step11/g11_6_18/gates_step11_full.json` and `.../selftest_full.json`.

**11.7 — stays WITHDRAWN and was NOT revived at closure.** It is a rendering, never a result, so it
adds nothing to the board, and its re-pointed `D-EU-88` district-viewer input still does not exist.

🔴 **What is owed after this step: nothing computed.** `D-IMP-4` (2026-09-03) deleted Step 12 —
**the pipeline is Steps 0–11** — so there is no downstream consumer of Step 11's
`appliance_electricity`/`dhw` output to hand it to. The open question recorded at last+261 and last+263
(*“what consumes Step 11's output next”*) is therefore **answered by the parent plan rather than by the
author: nothing does.** What follows is the cross-step analysis and the manuscript.

⚪ **Two honest caveats on this entry.** (1) It is written **retrospectively** from the closure records
and `Prompts/RESUME.md`, not from a live log kept at the time — which is exactly the defect it records.
(2) Both stock-scale populations are **`C2` cells that `R8` still refuses `--scored`**; Step 11's own
`G11.x` board is scored, but **no `G10N.x` UBEM result is claimed from them here**.
