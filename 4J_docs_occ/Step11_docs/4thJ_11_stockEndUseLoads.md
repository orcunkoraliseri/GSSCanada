# Step 11 — Activity-driven end-use loads at stock scale

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 11. Validation: `4thJ_11_stockEndUseLoads_val.md`
#### Basis: `../Step10_docs/4thJ_10_ubemRealStock.md`. Predecessor (closed): `../Step9_docs/4thJ_09_enduseLoads.md`

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
| **11.3** | **Per-dwelling trigger campaign** — run the trigger on Step 10 Arm D's `N_u` diaries per building | Step 10 items 10.4, 10.6 | no |
| **11.4** | **Accounting-path resolution** — one path per end-use per building, recorded in the manifest (§3) | 11.3, Step 10 10.6 | no |
| **11.5** | **Stock-scale aggregation** — `G11.12` at real neighbourhood scale, with the population declaration `G11.16` requires | 11.3, 11.4 | no |
| **11.7** | ⚪ **3D stock visualisation, ONE static self-contained `.html`** — added 2026-08-28 at the author's request. Renders the Step 11 stock aggregate on the **existing** OpenUBEM 3D export `OpenUBEM/docs/docs_ACTIVE/europeanLocations/outputs_3D`, in the vocabulary and conventions of `OpenUBEM/docs/docs_EXPLANATION/OpenUBEM_fundamentals.md`. 🔴 **It is a rendering, never a result, and it inherits every bar**: Arm D and Arm F **never share a colour scale or a legend** (`G10.9`); every Arm F surface is labelled a **LOWER BOUND** with **no magnitude attached** (`G10.22`); **no per-dwelling value is rendered at any zoom** (`G11.13`); every figure is **HEATING-ONLY** and stated **relative to its own control** (`G10.12`); the **Lyon geometry provenance** is printed on the page (`G10.11`). ⚪ **Read-only on the OpenUBEM tree** — it reads the export and never writes into it. No new simulation, no new artefact in their tree | 11.5 | no |
| **11.6** | **Gate board, mutation battery, dossier** — every `G11.x` seen failing its designated mutation, `ALREADY_FAILING_AT_BASELINE` where §1.4 applies | 11.5 | no |

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
