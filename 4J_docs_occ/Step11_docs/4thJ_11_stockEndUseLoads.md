# Step 11 — Activity-driven end-use loads at stock scale

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 11. Validation: `4thJ_11_stockEndUseLoads_val.md`
#### Basis: `../Step10_docs/4thJ_10_ubemRealStock.md`. Predecessor (closed): `../Step9_docs/4thJ_09_enduseLoads.md`

---

## STATUS

⚪ **PLANNED, 2026-08-26. Nothing built.** Depends on Step 10, which depends on the OpenUBEM
European-locations arc.

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
| **11.1** | **Carry-over audit** — the Step 9 mapping, trigger and citation set re-scored unchanged on the new basis; `G11.1`–`G11.4` | Step 9 artefacts | no |
| **11.2** | **🔴 `G9.7` diagnosis** — falsify candidate explanations for the 2–4× DHW magnitude **before** re-measuring (§1.3) | Step 9 artefacts | no |
| **11.3** | **Per-dwelling trigger campaign** — run the trigger on Step 10 Arm D's `N_u` diaries per building | Step 10 items 10.4, 10.6 | no |
| **11.4** | **Accounting-path resolution** — one path per end-use per building, recorded in the manifest (§3) | 11.3, Step 10 10.6 | no |
| **11.5** | **Stock-scale aggregation** — `G11.12` at real neighbourhood scale, with the population declaration `G11.16` requires | 11.3, 11.4 | no |
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
