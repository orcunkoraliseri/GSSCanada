# 3J Leg-3 — v4 implementation plan: **what is actually left of the leg**

**Opened 2026-08-06**, immediately after v3 closed 6/6, and opened **because the user asked where the
open items were** and the honest answer was *nowhere*.

---

## 0. Why this round exists — and it is the same defect twice

v2 ended with three decisions carried as a **bullet list**. v3 existed to fix exactly that, under the
banner *"a bullet list is not a task — it has no test method and nothing that fails if it is
ignored."* v3 then closed, and I wrote the next five open items **as a paragraph**: in a superseded
manager prompt, in the backward-audit document, in memory files, and finally as prose in a scope band
on the board.

🔴 **Same failure, one level up, by the same author, the same day.** `B-13` appears in eight files and
is a task in none of them. `LAUNDRY` likewise. Neither has a state, an owner, a test method, or
anything that fails if it is ignored.

🔴 **And the ledger check could not see it.** `j3_ledger_check.py` verifies that every *owed* item is
visible in the plan, the prompt and the board. With v3 closed there were **no owed items**, so all
four conditions were satisfied by an empty set — the vacuity recorded in v3 §2.4, biting one entry
later. **The check was green and the board was misleading at the same time, and neither contradicted
the other.** A reader caught what the checker structurally could not.

**v4's first purpose is therefore to make the ledger check live again.** Five owed items exist; the
check now has something to fail on.

---

## 1. Status panel

*Opened **2026-08-06** and **worked to the end the same evening**: A2/A3 closed, four decisions taken,
then A4 executed, B2 measured, and **B1 and B3 both withdrawn as never-open**.
~~**4 done · 1 partial · 2 withdrawn · 1 decision · 2 blocked** of 10.~~*

**UPDATED 2026-08-06 (evening) — `V4-C1` decided and executed, `V4-C2` checked and still blocked,
`V4-C3`'s prompt written, and a NEW item `V4-B4` opened and closed the same night.
7 done · 2 withdrawn · 2 blocked of 11. Nothing is owed by the user.**

```
DONE        7 / 11   ← V4-A1 (decided, §4.1) · V4-A2 (§2.2) · V4-A3 (§2.3) · V4-A4 (§2.4, EXECUTED)
                       V4-B2 (652 runs re-read; 3 of 8 verdicts move) · V4-C1 (5 lines, one severity)
                       V4-B4 (6,000 runs re-read; the 2J manuscript's own table)
WITHDRAWN   2   ← V4-B1 (decided V2-B4 + run V2-D10, 08-05) · V4-B3 (falsified + withdrawn V2-A1, 08-04)
DECISION    0   ← nothing is owed by the user; V4-C1 was taken and executed 2026-08-06
BLOCKED     2   ← V4-C2 (cluster — RE-CHECKED under the amended Speed rule, block SURVIVED)
                  V4-C3 (data access — deep-research prompt V07 written; still blocked)
```

> 🔴 **`V4-B4` did not exist this morning.** It was opened because the user stated the 2J paper is
> **not submitted** — my record said it was — and it is the largest single result of the round: the
> manuscript's own EUI table is wrong in **every** cell, and **three of its four band verdicts change**.
> §2.8, and `V4-B4_PREREGISTRATION.md` / `V4-B4_RESULTS.md`.

> 🔴🔴 **Two of the four decisions taken on 2026-08-06 were never open.** `V4-B1` had been decided in
> `V2-B4` and **executed** in `V2-D10` on 2026-08-05; `V4-B3`'s finding had been **falsified and
> withdrawn** by `V2-A1` on 2026-08-04 (*"B-13 does NOT reach the submitted paper. No erratum is
> owed."*). **Both were written into v4 from prose without re-reading the v2 plan**, and both were put
> to the user as questions that already had answers. §2.5, §2.7.

| | id | task | kind | blocks | state |
|---|---|---|---|---|---|
| ✅ | **V4-A1** | Hotel EUI: which rule, on a **bimodal** population | decision | `S9-EUI-hotel` | **DECIDED** — per-geometry split (§4.1) |
| ✅ | V4-A2 | Office EUI: band-basis limitation, with its number | desk | — | **DONE** · digits re-derived by A4 |
| ✅ | V4-A3 | Retail EUI: the one genuine injection effect, quantified | desk | — | **DONE** · digits re-derived by A4 |
| ✅ | **V4-A4** | Score `S9-EUI-*` under the authorised split | desk | — | **DONE** — 🔴 both predictions inverted, cause found |
| ⬛ | ~~**V4-B1**~~ | ~~`LAUNDRY`: per-object resize, or leave the global K~~ | — | — | 🔴 **WITHDRAWN — never open** (§2.5) |
| ✅ | **V4-B2** | Leg-2's published EUI is inflated — **all 8 rows, not 4** | desk | a closed paper | **DONE** — 652 runs re-read; **3 of 8 verdicts move** |
| ⬛ | ~~**V4-B3**~~ | ~~`B-13` reaches the **submitted** 2J manuscript~~ | — | — | 🔴 **WITHDRAWN — the premise is false** (§2.7) |
| ✅ | **V4-B4** | The **2J manuscript's own** EUI table — different campaign, same defect | desk | the paper | 🔴 **DONE** — 6,000 runs re-read; **3 of 4 band verdicts change** (§2.8) |
| ✅ | **V4-C1** | Retail quarantine: one cause, ~~two~~ **five lines**, two severities | decision | scorecard | **DECIDED + EXECUTED** — all five now FAIL |
| ⚫ | V4-C2 | `RW9` is in the code and not in the shipped Step-4 report | work | — | **BLOCKED — re-checked, block survived** |
| ⚫ | V4-C3 | QC hotel occupancy is Power-BI-locked | work | hotel AB/QC | **BLOCKED** — prompt `V07` written |

> 🔴 **One decision is still owed: `V4-C1`.** Four were taken on 2026-08-06 (§4); **one of those four,
> `V4-B1`, has since been withdrawn because it was not an open item** — it was decided in `V2-B4` and
> executed in `V2-D10` on 2026-08-05, and its result is in the frozen deliverable. §2.5.
>
> 🔴🔴 **Executing `V4-A4` falsified both of its own pre-registered sub-verdicts, and the cause was the
> input file.** A2/A3/A4's predictions were computed from `Step9_docs/outputs_step9/` (2026-07-31)
> instead of the frozen `outputs_step9_deliverable/` (2026-08-06 00:05). **Office and retail move by
> ~0.1 %; hotel inverts** — 203.33–318.42 with 28 cells **over the 300 ceiling**, not 147.87–209.43
> under the 180 floor. ⚠️ **`V4-A2`'s "the document is inverted in three places" is therefore
> RETRACTED: the document was right and my correction was the imported number.** §2.2, §2.4 and
> `V4-A4_split_scorecard.md`.
>
> ⚠️ **A1 being decided did not move a gate, and neither did executing it.** All three `S9-EUI-*`
> remain **FAIL**; `step9_gates.json` is untouched in both directories.

---

## 2. The tasks

### V4-A1 — Hotel EUI: which rule, on a population that is bimodal

**This is where the v3-H3 trigger lands, and there is a third option neither of us put on the table.**

`S9-EUI-hotel` band `[180, 300]`, all-cells rule, currently **FAIL**. The v3 decision left the rule
unchanged and left the trigger with the user. Two things are now on the record:

1. **The rule's own citation was false** (v3 §2.3). Leg-2 scored these values on the **median** and
   graded a miss **WARN**; Leg-3 tightened both and recorded neither. That is a real argument for
   restoring Leg-2's convention.
2. **Restoring it as a package moves three statuses** — office FAIL→WARN, retail FAIL→WARN, hotel
   FAIL→PASS — and *a basis change that turns FAIL into WARN is a band change in disguise* (R1).

🔴 **The third option: the hotel population is bimodal and neither rule describes it.**
**Measured 2026-08-06 from the artefact** (V4-A2/A3; the first draft of this section quoted the ranges
from memory and had them slightly wrong — corrected here and on the board): `SuperTall`
**147.87–162.76**, `Tall` **193.83–209.43**, and the largest gap between consecutive sorted values is
**31.07 kWh/m² — 25.9 % of the band's own width.** 🔴 **The 180 floor lies inside that empty gap**, so
no cell can land near the threshold and the median (**178.29**) describes **no building in the set**.
`all_cells` scores two populations as one. **Both rules answer a question the data does not pose.**

🔴 **And the sharper fact, which arrived with A2/A3: the gate cannot see occupancy at all.**
Injecting the occupancy model moves the hotel channel by **+0.06 to +1.45 kWh/m² (≤ 0.70 %)** in every
group — against a 31.07 gap. **`S9-EUI-hotel` returns the same verdict with and without the thing it
is named for.** It is a geometry classifier that is currently *blocking*. Whatever is decided here,
that is the fact it should be decided on.

**Candidate resolution, stated so it can be attacked:** score the hotel channel **per geometry**, so
Tall and SuperTall are graded separately against the same band. **This is not a free move and must not
be taken quietly** — it changes the gate's unit, and a unit change chosen after seeing which unit
passes is gate-shopping under a different name.

**Test method, pre-registered before any rescoring:**
- Derive the split from **geometry**, which is a design variable fixed before any EUI existed — not
  from a clustering of the EUI values themselves.
- **Write down both sub-verdicts before scoring**: if Tall passes and SuperTall fails, the answer is
  *the gate was hiding a real geometry defect*, and the scorecard gains a FAIL rather than losing one.
  **If the split cannot produce a FAIL it must not be adopted.**
- Apply the identical treatment to office and retail. A rule that is only applied where it helps is
  the thing this project refuses.

**Expected result — now known, and the pre-registration's condition is MET.** The split gives
`Tall` **PASS** (193.83–209.43, inside [180,300]) and `SuperTall` **FAIL** (147.87–162.76, ~17 % under
the floor). **So it can produce a FAIL, which was the bar for adopting it at all** — it converts one
blurred failure into one clean pass *and* one sharper, correctly-attributed failure. ⚖️ **Stated against
it:** the split makes the gate an honest **geometry** classifier, and an honest geometry classifier is
still not an occupancy gate. It does not make `S9-EUI-hotel` informative about this project's subject.

**Owed decision:** (a) pull the v3-H3 trigger as written, (b) leave the rule alone, or (c) authorise
the per-geometry investigation above under its pre-registration.

✅ **DECIDED 2026-08-06 — (c), the per-geometry split, under the pre-registration exactly as written
above.** Recorded reason in §4.1. **The decision authorises the scoring; it does not perform it** —
that is `V4-A4`, now READY. **No band value moves**; the band stays `[180, 300]` and is applied
unchanged to both sub-populations.

---

### V4-A2 — Office EUI: write the band-basis limitation, with the number

**READY — desk work, no simulation, no decision.** Direction change of 2026-08-04 applies: *stop
running arms for `S9-EUI-*`; the uninjected control proves none of the three blocking gates is an
occupancy problem, so all unblocking work is desk work.*

The number already exists and it is the load-bearing one: the **`Default_NECB` control** — NECB's own
schedules, no injection, same geometry, envelope, climate and plant. ~~reads **85.29 kWh/m² against a
floor of 100**, so roughly **15 of the 22** predates any occupancy model~~ ⚠️ **Struck 2026-08-06: those
are arm-A figures, not Step 9's.** On the Step-9 artefact the control reads **81.70–90.33** across the
four groups — **all below the 100 floor** — the total gap is **26–37**, and the split is closer to
**half and half**. The band comes from **standalone prototypes**; this is a channel stacked inside a
shared tower.

**Deliverable:** a limitation written into the pipeline document, quoting the control, stating that
`S9-EUI-office` measures band applicability more than it measures the occupancy model.
**Not a gate edit, not a band edit.** The gate stays FAIL.

**Test method:** the limitation must name the control cell and its value, so a reader can re-derive
it from `step9_eui_by_channel.csv` without trusting the prose.

---

### V4-A3 — Retail EUI: the one genuine injection effect

**READY — desk work.** Retail is the only channel where the uninjected control **is in band**
(`Default_NECB` retail passes everywhere); the failures are the 2030 bundles and the `sens` cells in
CLG. **So retail's FAIL is 100 % an injection effect** — the only one of the three that is a
statement about the occupancy model at all.

**Deliverable:** quantify which cells fail and by how much, and say plainly that this one is ours.
**Test method:** the cell list must be derived from the artefact, and the count must match
`step9_eui_by_channel.csv`; a claim of "N cells" that cannot be re-derived is not accepted.

---

### V4-A4 — Score `S9-EUI-*` under the authorised split — ✅ **DONE 2026-08-06**

**Result: `improvements/v4/V4-A4_split_scorecard.md` · `v4_a4_split_scorecard.json` · generator
`a4_split_score.py`.** Desk work: one CSV read, one new file written, **`step9_gates.json` not touched
in either directory**, no band edit, no simulation, cluster not contacted.

| channel | rule in force | SuperTall | Tall | pooled (as shipped) |
|---|---|---|---|---|
| office | `all_cells` | FAIL (0/28 in band) | FAIL (0/28) | FAIL |
| retail | `median` | FAIL (median 74.99) | FAIL (median 76.47) | FAIL |
| **hotel** | `all_cells` | **PASS** (28/28 in band, median 210.45) | **FAIL** (28/28 over the ceiling, median 310.15) | FAIL |

🔴 **Fence 1 fired: both pre-registered sub-verdicts are wrong, and inverted.** They read `Tall` PASS /
`SuperTall` FAIL. **The cause is the input file, not the reasoning** — the predictions were computed
from `Step9_docs/outputs_step9/` (2026-07-31), not from the frozen deliverable
`outputs_step9_deliverable/` (2026-08-06 00:05, named in `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`).
Re-running the identical scoring on the superseded file **reproduces both predictions exactly**, which
is the proof rather than the excuse. The superseded directory predates **`V2-D10`**, the per-object
`LAUNDRY` resize that moved this channel, and the inversion **was already on the record** in
`3rdJ_L3_manager_prompt_2026-08-06_v2_close.md` §V2-E5: *"the failing end inverted while the count held
still."* **Both artefacts say 28 of 56 — the count is what made the substitution invisible.**

✅ **Fences 2–4 held.** At least one hotel sub-gate still FAILs (`Tall`, 28/28 over the ceiling) so the
split **does not clear a blocker** (R1); all three channels were scored, and the split **buys nothing
for office or retail** — that is the reported result; and the whole task was desk work.

**The split is adopted for hotel**, on a finding that is *larger* on the canonical data: the empty gap
between the two geometry clusters is **84.64 kWh/m²/yr = 70.5 % of the band's own width**, the **300
ceiling sits inside it**, and the pooled median 260.54 describes no building in the set. ⚖️ **And the
limitation survives its own decision:** both `Tall` controls are already over the ceiling and both
`SuperTall` controls already in band **before any occupancy is injected**, which moves each cell by
**≤1.00 %**. Better attribution; **still not an occupancy gate.**

---

**The pre-registration as it stood, kept verbatim so the fences can be audited against the result
above.** (Earlier states: BLOCKED on V4-A1 → READY on the A1 decision of §4.1 → DONE.) The bar it had
to clear:

- The split is applied to **all three** channels, not only hotel. Office and retail are re-expressed
  per geometry too; if that changes nothing for them, that is the reported result, not a reason to
  skip them.
- Both hotel sub-verdicts were written down **before** the decision: `Tall` **PASS**, `SuperTall`
  **FAIL**. If the executed scoring disagrees with either, **the discrepancy is the finding** and the
  split is not adopted until it is explained.
- **The scorecard must not lose a FAIL.** `S9-EUI-hotel` currently FAILs; after the split at least one
  hotel sub-gate must still FAIL, or the split has cleared a blocker and must be reverted (R1).
- Desk work off `step9_eui_by_channel.csv`. **No simulation, no band edit, no re-run.**

---

### V4-A5 — What `S9-EUI-hotel` is actually failing on — ✅ **DONE 2026-08-06**

**Full write-up: `improvements/v4/V4-A5_hotel_archetype_separation.md`** · generator
`a5_hotel_archetype_split.py` · data `v4_a5_hotel_split.json`.

**Aim.** `V4-A4` measured the split and stopped. It left the two questions a reader asks next: *why*
the geometries separate, and *what the gate is failing on* given that the uninjected control already
fails it. Both are answerable from the frozen deliverable's Step-8 end-use table, on this machine.

**Two claims, both falsifiable, both written before the decomposition ran:** (C1) the separation is
carried by **one** end use, not spread across the load — if it is spread, there is no single-object
story and the archetype reading fails; (C2) that end use **does not respond to occupancy** — if it
moves across the 14 scenarios by more than the gap, C1 is not an archetype story at all.

**Result — both held, and harder than expected.**

| | measured |
|---|---|
| separation carried by `dhw` | **79.04 of the 84.64 kWh/m² gap = 93.4 %** (109.39 → 188.43) |
| next largest | `interior_equipment`, +20.27 · then nothing above 2.7 |
| `heating` | **−3.70** — *lower* in the building with the higher EUI; no envelope story fits |
| `dhw` movement over all 14 scenarios | **0.01 kWh/m²** |
| largest occupancy movement, any end use | `interior_lighting`, **4.34** on a ~310 total (**1.4 %**) |
| hotel floor area | `Tall` is **exactly half** `SuperTall` (14,215.4 vs 28,430.8 m², ratio **2.000**) |
| DHW energy | `Tall` is **86.1 %** of `SuperTall` (2,678,643 vs 3,110,136 kWh, ratio **1.161**) |
| uninjected `Default_NECB`, `Tall` | **304.41 / 315.82 — over the 300 ceiling with no occupancy model in the building** |

🔴 **The mechanism: one DHW load sized per building, divided by a floor area that halved.** The EUI
difference is a denominator artefact, not a difference in use. **Same shape as the `LAUNDRY` finding**
— one object that does not scale with what it is normalised by. Second instance, different object.

**Guard, and it is the point of the task.** The decomposition is required to reconstruct
`eui_CFA_kWh_m2` — the exact column Step 9 scores — before anything is read into it. It does, to
**1.1 × 10⁻¹³ kWh/m²** across all 56 hotel cells; the script asserts this and stops otherwise. A
look-alike quantity would have produced the same story and been worthless.

⚠️ **Not a bimodality result, and it must not be written as one.** Two geometries cannot distinguish
"the distribution has two modes" from "we ran two archetypes and they differ" — vacuous-reading class
#16 at n = 2. **The defensible claim is the mechanism, not the shape of the distribution.**

**No gate is re-scored, no band moves, nothing outside `improvements/v4/` is written except caveats 11
and 12 in the Step-9 master document.**

---

### ~~V4-B1 — `LAUNDRY`: per-object resize, or leave the global K~~ — 🔴 **WITHDRAWN 2026-08-06: it was never an open item**

**This task should not have existed, and the decision recorded for it on 2026-08-06 (§4.2) decided
something that had already been decided *and already run* the day before.**

| | where | when | what |
|---|---|---|---|
| decision | **`V2-B4`** | **2026-08-05** | *"per-object resize: `LAUNDRY` alone at K ≈ 7, other 15 heaters K = 1"* — global K refuted |
| execution | **`V2-D10`** | **2026-08-05 eve** | implemented, run **locally on win32**, D1–D5 PASS / D6 FAIL as pre-registered, **CLOSED** |
| shipped | frozen deliverable | 2026-08-06 00:05 | spec `Laundry Service Water Use 30.6gpm 180F=**8.5**`, every other burner K = 1 |

**The instrument in the deliverable is not even B4's K ≈ 7.** D6 was a genuine falsification: K ≈ 7 was
refuted by its own test and **replaced by a measured 8.5 rather than a rounded 7**. `V2-D10`'s
discriminator D5 is the measurement the whole argument needed — `LAUNDRY`'s own slope of ln E against
ln V went **0.0182 → 0.3051** under K = 7 applied to the one object, against **0.0312** under a global
K = 6. *Six times the capacity applied globally moved it by 0.013; seven times applied to the one
object moved it by 0.287.*

**Measured consequences, already on the record (`V2-E5`):** hotel DHW **+120.09 %** (predicted +112),
and the resize is **not channel-confined** — residential DHW −2.76 %, office −0.66 %, retail −0.27 %:
the pinned burner was being cross-subsidised by its neighbours on the loop. **All three blocking gates
still FAILed and 0 gates changed status.** It also moved `S9-EUI-hotel` from *28 below the floor* to
*28 above the ceiling* — the inversion that then broke `V4-A4`'s predictions (§2.4).

🔴 **So the two claims v4 carried about B1 were both false.** *"It is an owed decision"* — it was taken
on 2026-08-05. *"Nothing runs; execution is BLOCKED on compute and the stay-local rule"* — it had
already run, locally, on this machine, without the cluster. **§4.2 is struck and this item is
withdrawn, not closed**; nothing about the deliverable changes.

⚠️ **This is the round's own founding defect, in its fourth instance and at a new depth.** v2 → v3 was
*a bullet list is not a task*; v3 → v4 was *the same thing one level up*; and v4 has now produced **a
task manufactured out of prose describing work that was already finished.** The item was written from
the `LAUNDRY` paragraphs in memory and the audit document — **none of which were re-checked against
`3rdJ_L3_v2_implementation.md`, where lines 372 and 393 record both the decision and its closure.**

**Reopen trigger.** If the `8.5` spec is ever revisited, it reopens as a **`V2-D10` follow-up with the
D1–D6 pre-registration attached**, not as a fresh decision. **A new round may not restate a closed v2
item as open without citing its v2 row.**

---

<details><summary>Original V4-B1 text, kept verbatim — it is accurate about the physics and wrong only about the state</summary>

**Owed decision.** The K=1 vs K=6 campaign (112/112 cells, local) showed the hotel DHW elasticity is
**0.334**, outside its own predicted interval, and that **the mechanism is one object**: at K=6 every
heater except `LAUNDRY` has slope **exactly 0.000**; `LAUNDRY` has slope **−0.98 in both arms**, i.e.
delivered energy is constant regardless of draw. It is capacity-pinned at K=1 *and* at K=6.

The global K was chosen on a volume-weighted aggregate that is **61–69 % `LAUNDRY`** — so it sized 16
objects by the factor that fixes one, oversizing 15 already-correct heaters. Internal reference:
`BOOSTER`, same 180 °F design, never clipped. `LAUNDRY` alone needs **K ≈ 7**.

**Recommendation on record: per-object resize.** It is a user decision because it changes plant sizing
and would require a re-simulation, which the standing rules do not permit me to launch.

~~✅ **DECIDED 2026-08-06 — per-object resize is the instrument.** Recorded reason in §4.2.
🔴 **Nothing executes.** The decision names the correct instrument and retires the global K as the
sizing basis; the run itself needs compute, and the standing rule is **stay local — Speed is not
contacted at all**. State is therefore **DECIDED, execution BLOCKED**, and the published `K=6`
elasticity result **keeps its result and gains a stated instrument limitation** rather than being
withdrawn. **No sizing value is changed in any IDF by this decision.**~~
🔴 **Struck — see the withdrawal above. It had been decided (V2-B4) and executed (V2-D10) on
2026-08-05, locally, without the cluster.**

</details>

---

### V4-B2 — Leg-2's **published** office EUI is inflated ~1.706×

**Owed decision, and it touches a paper-ready leg.** `calculate_eui()` filters on `TableName` and
**never on `ReportName`**, and EnergyPlus emits a table of that name under both
`AnnualBuildingUtilityPerformanceSummary` (**GJ**) and `DemandEndUseComponentsSummary` (**W**). The
unit guard skips only water, so every **watt** row is summed as if it were a kWh. Measured on a real
v24.2.0 SQL: 7,837,731 kWh legitimate + 5,533,372 W read as kWh → factor **1.706×**.

Corroboration: Leg-2's three archetype medians (172.6 / 172.5 / 172.7) are implausibly tight for three
different use profiles across six cities. **Leg-3 is not affected** — it uses its own meter-sum method
with attribution residual 0.000000 %.

**The decision is not technical.** The fix is one clause. The consequence is that a **closed,
paper-ready leg** has a wrong published number. Options: correct and re-publish, correct and carry an
erratum, or document without reopening.

✅ **DECIDED 2026-08-06 — quantify from local outputs first, then choose between erratum and
re-publication with the magnitude in hand.** Recorded reason in §4.3. **This is not a deferral of the
disclosure decision; it is a refusal to take it on a factor rather than on the affected numbers.**

**Test method, pre-registered:**
- Re-derive office EUI for Leg-2 cells with a `ReportName`-filtered sum, from **local** artefacts only.
- 🔴 **If the required SQL/HTML outputs are not on this machine, the item becomes BLOCKED and is
  reported as blocked** — it is not silently downgraded to "documented", and Speed is not contacted
  to fetch them.
- The 1.706× factor is an **as-measured single-cell** figure. What must be reported is the range
  across the affected cells, and explicitly whether any published *conclusion* (not just a number)
  moves. **"The factor is uniform" is a claim to be shown, not assumed.**

#### ✅ EXECUTED 2026-08-06 — **PARTIAL**. Full write-up: `improvements/v4/V4-B2_defect_reach.md`

Generator `b2_eui_defect_reach.py`, data `v4_b2_defect_reach.json`. Read-only on `Leg2_2-split/`.

1. 🔴 **The reach is larger than the finding said. It is not office-only.** `_eui_from_sql()` →
   `calculate_eui()` is called on **both** branches of the aggregator — residential at
   `3rdJ_08_simulation_2split_agg.py:438` and office at `:481` — and both write the same
   `eui_kWh_m2` column that `build_eui()` medians. **All eight published rows are contaminated**, the
   four residential archetypes as well as the four office groups.
2. 🔴🔴 **"The factor is uniform" was tested and REFUTED.** Measured on all 12 Leg-2 `eplusout.sql`
   present locally: **1.4868 – 1.7601, an 18.4 % spread.** The factor tracks the **household**, not
   the campaign arm — it is the ratio of the building's peak demand to its annual energy. **So
   `172.7 ÷ 1.706` is not a valid correction**, and a factor measured on dwellings says nothing
   reliable about the office tower.
3. 🔴 **A published conclusion moves, and for two rows it moves whatever the factor.**
   `resid OtherDwelling` (140.0) and `resid HighRise` (143.0) fall **below** their band floors under
   every factor in the measured range — two published PASSes lost. **The sole published WARN can go
   either way**: `SingleD` 211.7 is currently **above** the SHEU ceiling; corrected it is either
   **inside the band** (WARN → PASS) or **below the floor** — out of band at the opposite end.
   *The same inversion shape as `S9-EUI-hotel`.* Office `172.5–172.7` brackets to **98.0–116.2**, so
   the 100 floor lies inside the plausible range and `G2o` PASS is not safe either.
4. 🔴 **BLOCKED, and reported as blocked, exactly as this test method pre-registered.**
   `outputs_step8/office/` is **empty**, `office_idfs_v242/` holds **4 IDFs and no results**, and
   **no Leg-2 office SQL exists on this machine.** The 12 local SQL are residential smoke cells, not
   the campaign cells behind the published medians. The corrected values need the campaign SQL, which
   is on Speed. **Not downgraded to "documented"; the cluster was not contacted.**

⚠️ **The disclosure route is still not chosen, and now cannot be chosen on a divisor.** What §4.3
asked for is delivered — the reach, the mechanism, the refutation of uniformity, and the fact that at
least two published in-band results do not survive correction. 🔴 **Until the campaign SQL is
reachable, no Leg-2 EUI figure may be quoted as corrected — and none may be quoted as sound.**

#### 🟢 UNBLOCKED AND MEASURED — office half, same day. Write-up: `improvements/v4/V4-B2_corrected.md`

**Point 4 above was blocked on a reading of the standing rule, not on a resource.** Hours after it was
written the user amended it: *"tu peux obtenir ce que choses tu veux sur le speed, mais tu ne peux pas
utiliser pour des simulations."* **Retrieval permitted, execution not.** All 252 published office runs
were pulled one at a time with `scp`, read locally with `sqlite3`, and deleted before the next — peak
disk one file, **no `sbatch`, no `srun`, no login-node `python`, no simulation.**

**Guard first.** Step-9's `build_eui()` median arithmetic reproduced on the *shipped* column returns
**172.66 / 172.62 / 172.54 / 172.72** against published 172.7 / 172.6 / 172.5 / 172.7. ✅ Same
population. **252 of 252 runs; 3 first-pass `scp` failures all retrieved on retry; nothing estimated.**

| published row | n | published | **corrected** | verdict |
|---|--:|--:|--:|---|
| office all | 252 | 172.7 | **106.56** | IN → **IN** |
| office Knowledge | 84 | 172.6 | **106.66** | IN → **IN** |
| office Public | 84 | 172.5 | **106.71** | IN → **IN** |
| office Sales | 84 | 172.7 | **106.56** | IN → **IN** |

1. 🟢 **No office verdict moves.** Point 3's *"G2o PASS is not safe either"* is **falsified for office**
   — measured, they stay in. The bracket said 98.0–116.2 and could not choose; the answer is 106.6.
2. 🔴 **Uniformity refuted harder: 1.5182 – 1.9075, a 25.6 % spread**, running *past* the top of the
   residential range. Point 2's warning that a dwelling factor says nothing about the tower is
   confirmed: `172.7 ÷ 1.706 = 101.2`, and the measured answer is **106.56** — the shortcut lands the
   right verdict for the wrong reason, 5 % off, with no way to know it.
3. 🔴 **The mechanism is now measured, not inferred.** The factor is flat across the **7 occupancy
   scenarios** (medians 1.6488–1.6550, **0.4 %**) and swings **17.6 %** across the **6 climate zones**
   (5C 1.571 → 7A 1.847); within one cell it is constant to ~1 %. **It is a building-and-weather
   quantity. Occupancy does not touch it.**
4. 🔴 **The median passes and a fifth of the population does not.** Per-run corrected EUI spans
   **93.51 – 117.91**; **50 of 252 runs (19.8 %) fall below the 100 floor.** Under Leg-3's `all_cells`
   rule this population **fails**; Leg-2 scored the median, and that is the rule it is scored under.
   **Recorded because it is true, not because it changes the verdict.**
5. ⚠️ **Scenario comparisons: no claimable one flips.** Of 756 within-cell scenario pairs, 113 change
   sign — **every one with a shipped gap ≤ 1.13 kWh/m²** (median 0.20), while **all 128 pairs with a
   larger gap keep their direction.** But **magnitudes do not survive**: any absolute effect size in
   the office section is inflated by the same ~1.65×.
6. 🔴 **`V4-B2_defect_reach.md` §5's open question is answered and one candidate is dead.** The three
   subtype medians were suspiciously tight (0.18 kWh/m²). Corrected, they are **tighter — 0.144.**
   **The contamination was not compressing them.** The three office occupancy profiles genuinely
   produce near-identical annual EUI. Recorded as a finding about the model, not explained here.

~~🔴 **The residential half is NOT covered by any of this** and is running under its own
pre-registration (`V4-B2_PREREGISTRATION_resid_sample.md`). **The §0 disclosure paragraph in
`V4-B2_corrected.md` is the office half only and must not be sent alone.**~~

#### 🔴🔴 RESIDENTIAL HALF — same day. A pre-registered prediction FAILED and a SECOND defect appeared

**Write-up: `improvements/v4/V4-B2_corrected_resid.md`** · defect statement:
`V4-B2_defect_reach.md` §8 · generators `b2_resid_corrected.py`, `b2_resid_two_defects.py`.
**400 of 400 runs retrieved (100 per archetype, pre-registered sample of 2 100 each), zero failures.**

**Guard first: P3 PASSES on all four** — shipped sample medians 211.10 / 178.38 / 140.11 / 145.46
against published 211.7 / 177.5 / 140.0 / 143.0, worst error **+1.72 %** inside a ±2 % tolerance.

| published row | published | defect 1 only | **both defects** | 95 % interval | movement |
|---|--:|--:|--:|---|---|
| `HighRise` | 143.0 IN | 101.23 | **101.23 BELOW** | 99.38 – 104.77 | 🔴 **MOVES** |
| `MidRise` | 177.5 IN | 128.21 | **128.21 IN** | 125.05 – 131.18 | same |
| `OtherDwelling` | 140.0 IN | 139.88 | **124.98 BELOW** | 121.56 – 130.42 | 🔴 **MOVES** |
| `SingleD` | 211.7 **ABOVE** | 210.86 | **130.57** | 126.60 – 134.86 | 🔴🔴 **INVERTS** |

1. 🔴 **P1 is FALSIFIED.** It predicted `HighRise` **and** `OtherDwelling` fall below their floors under
   the defect-1 correction. `HighRise` does, clear by 12.7 with the whole interval below.
   **`OtherDwelling` gives 139.88 — IN.** `V4-B2_defect_reach.md` §3's *"BELOW, either way"* is
   **WITHDRAWN for that row.** A prediction naming two rows and getting one is a failed prediction.
2. 🔴 **P2, no direction predicted: `SingleD` does not move under the defect-1 correction at all**
   (211.7 → 210.86, still ABOVE). §3 offered *"IN, or BELOW"* and the answer was **neither**.
3. 🔴🔴 **Why P1 failed is a SECOND defect in the same function.** The water guard is
   `if 'm3' in str(units): continue` (`plotting.py:319`) — **SI-only.** In IP output the water rows are
   `gal` / `gal/min`, which pass the guard and are summed as kWh. **The two defects are complementary:
   SI runs report demand in `W` (defect 1 fires, defect 2 cannot); IP runs report it in `kBtuh` and
   water in `gal` (defect 2 fires, defect 1 cannot). Every published run has exactly one of them.**
   Confirmed on one probe of each system, both factors reproduced arithmetically (1.000905, 1.314483).
4. 🔴 **Water counted as energy: 38.08 % of `SingleD`, 10.66 % of `OtherDwelling`, 0.00 % of the SI
   rows.** Over a third of the published `SingleD` EUI is gallons.
5. 🔴🔴 **THREE of the eight published rows change verdict** — two fall below their floors, and
   **Leg-2's sole published EUI WARN inverts.** `G2r` WARNs because `SingleD` overshoots the SHEU
   ceiling; corrected it sits at the *bottom* of the band. **The condition the WARN describes is not
   there.** Same inversion shape as `S9-EUI-hotel`.
6. ⚠️ **`SingleD` corrected is UNDETERMINED, not BELOW.** It misses the 130.6 floor by **0.03** inside
   an interval **8.3 wide**. What is determined: **no longer ABOVE.** No document may shorten this.
7. 🔴 **The factor separates by unit system, not by archetype — 1.0005 to 1.7541, a 75.3 % spread.**
   `V4-B2_defect_reach.md` §2's 18.4 % came from 12 local files that are **all SI**. Its *mechanism*
   survives; its *range* was measured on one side of a split nobody knew existed. **Reported as
   separation with a named cause, never as "bimodality"** — the `V4-A5` rule.
8. 🔴 **§3's direction was right for `OtherDwelling`; P1 still failed and stays failed.** §3 reached
   BELOW by dividing by 1.49–1.76; that row's real defect-1 factor is **1.002**, and it falls because
   **10.66 % of it is water.** Right verdict, wrong quantity. **A prediction is not confirmed by a
   mechanism discovered while investigating its failure** — logging only the half that came out right
   would be gate-shopping applied to a prediction instead of a threshold.
9. ✅ **The unit inventory guard fired and did its job.** `b2_resid_two_defects.py` prints every
   `(ReportName, Units)` pair **before** any total and refuses to vouch for a corrected number while an
   unclassified unit exists. **On its first run it refused, over `W` and `kBtuh`.** They were classified
   as power by hand, and two structural claims are now checked rather than assumed: **no power unit
   appears under the annual report** (so pinning `ReportName` does remove every watt) and **no energy
   unit appears outside it** (so pinning discards no real energy).
10. 🟢 **Leg-3 is immune to both defects, verified against the code path.**
    `Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py:554` builds EUI from the hourly
    `Electricity:Facility` / `NaturalGas:Facility` **meters** in Joules (`:343`), never from
    `TabularDataWithStrings`. A meter series carries neither a water row nor a peak-demand duplicate.
11. 🟢 **Office is unaffected by defect 2**, inferred from data already held: every one of the 252
    office factors is ≥ 1.5, and an IP run's factor is ~1.00, so **all 252 are SI and their water is
    `m3`**, correctly dropped by the shipped guard. Stated as an inference so it can be attacked.

🟢 **The §0 disclosure paragraph in `V4-B2_corrected.md` is now COMPLETE — all eight rows, both
defects, both scoring populations, with the `SingleD` undetermined verdict stated as undetermined.**
The office-only version is struck through above it and kept. **The erratum-versus-re-publication choice
is still the user's** (§4.3); this supplies magnitude, mechanism, and which conclusions move.

---

### ~~V4-B3 — `B-13` reaches the **submitted** 2J manuscript~~ — 🔴 **WITHDRAWN 2026-08-06: the premise is false**

**Full write-up: `improvements/v4/V4-B3_withdrawal.md`.**

**`V2-A1` settled this on 2026-08-04 and the v2 closure prompt states it in six words: *"B-13
withdrawn (no 2J erratum owed)."*** The transform is real and large — clip binds on **15.9 %** of
occupied slots, mean \|Δ\| **32.55 % of person-hours**, 32× the pre-registered threshold — **but it
lives in `21CEN22GSS_occToBEM.py`, which is not the converter behind the submitted paper.** The
production converter `2J_docs_occ_nTemp/07_aug_to_bem.py:97` takes the **mean** AT_HOME fraction and
contains no `occDensity` and no `.clip()`; the shipped 673 MB schedule CSV carries values in steps of
1/12, 1/10, 1/8 and 1/24, which is a member fraction and neither of the other two rules.

**And the manuscript already describes it correctly.** `readySubmission.md:231` carries the `V2-A2`
clause explicitly disambiguating the §3.5 mean from the §3.3 maximum. **So "described in neither
manuscript" is false of the current text**, and the 2026-08-13 hard stop was scheduling a notification
about a disclosure that is not owed. **The hard stop is cancelled.**

⚠️ **One small residual, checked rather than assumed.** The clause is in the `.md` (2026-08-04) and in
**no `.docx` on this machine** — `previous/readySubmission.docx` (2026-07-15) has both conflatable
sentences and not the disambiguation. **If the journal holds a `.docx`, it holds the ambiguous
version.** That is a clarity item for a revision round, not an erratum, it has **no deadline**, and it
is the user's call. 🔁 **Reopen trigger:** on any revision request, confirm the §3.5 clause is in the
file returned to the journal.

---

<details><summary>Original V4-B3 text, kept verbatim — every state claim in it is false</summary>

**Owed decision, and the most time-sensitive item here.** The backward audit's finding B-13 —
`occPre × (occDensity+1)` clipped — is present in **neither manuscript's** description of the method,
and it reaches the **already-submitted** 2J paper. **Submission does not make a finding go away**, and
the longer it sits the worse the options get.

**Options:** notify the journal now, hold until a revision request, or establish the magnitude first
and decide on that. **Recommendation: establish the magnitude first** — it is desk work and it is the
input every other option needs — **but that recommendation expires**, because "we were still measuring
it" stops being a reason at some point.

✅ **DECIDED 2026-08-06 — quantify now, then notify.** Recorded reason in §4.4. 🔴 **The second half
of that sentence is the decided part.** The failure mode this item already has on record is
measurement becoming the reason nothing is said, so the decision carries a **hard stop**:

- **The quantification is the only thing that is open-ended, and it is not open-ended for long.**
  Deliverable = the magnitude of `occPre × (occDensity+1)` clipping on the 2J published figures, from
  local artefacts.
- 🔴 **Expiry, written down: if the magnitude is not established by 2026-08-13, the notification goes
  out without it**, describing the transform and stating that the magnitude is not yet measured.
  **An unmeasured disclosure beats an unmade one on a submitted manuscript.**
- **Notification is owed regardless of magnitude.** A small magnitude changes the wording, not the
  fact that a transform present in the submitted pipeline is described in neither manuscript.
- Co-author notification is the user's action, not mine. My deliverable is the magnitude plus a
  drafted description of the transform. **I send nothing.**

</details>

---

### V4-B4 — the 2J manuscript's own EUI table — 🔴 DONE 2026-08-06, and it is the biggest result of the round

**Opened tonight, on a premise correction from the user:** *"ce publication pas soumit, donc nous
pouvons changer ce que chose nous voulons"* — **the 2J paper is not submitted.** My record said it was.
That single fact turns `V4-B2`'s disclosure question from *"erratum or re-publication?"* into
*"correct the manuscript"*, and it makes the manuscript's own numbers the thing that matters.

🔴 **The manuscript's numbers were never the numbers `V4-B2` corrected.** Table 5 reads
208 / 152 / 128 / 117 (full manuscript) and 200 / 170 / 115 / 128 (submission copy); Leg-2's Step-9
table reads 211.7 / 177.5 / 140.0 / 143.0. **Different campaigns entirely.** Applying B2's factors
would have been `V4-A1`'s error — reasoning about one artefact from another's figures — so nothing was
carried across and every number was re-derived from the manuscript's own campaign.

**Full detail: `V4-B4_PREREGISTRATION.md` (written before any corrected number existed) and
`V4-B4_RESULTS.md`.** In brief:

- **A census, not a sample.** The pre-registration planned 400 runs fetched from Speed because the raw
  outputs were assumed cluster-only. **All 6,000 are on this machine.** 6,000 of 6,000 recomputed,
  **zero guard failures.** *(The 400-run Speed fetch ran anyway and is retained as a cross-campaign
  check: 399/400, same conclusion.)*
- **Three guards, including one the defect cannot reach.** The corrected **electricity** total was
  checked against `elec_facility_kWh`, which is built from the **hourly meter stream** — a separate
  EnergyPlus output no version of `calculate_eui()` reads. **Max disagreement 0.067 %.**
- 🔴 **Q4, a pre-registered prediction, FAILED.** I predicted the campaign was uniformly SI. It is
  **3,000 SI / 3,000 IP**, split cleanly **by archetype** — not by year, not by city.
- **The mechanism is about unit magnitude, and it is exact.** `published = corrected + d1 + d2`,
  reconstruction error **0.0005 kWh/m²** over 6,000 runs. SI reports peak power in `W` (a big number)
  so the demand double-count carries 34–37 %; IP reports it in `kBtuh` (3.4× smaller) so it carries
  0.1 %, while IP water in `gal` carries **40.8 %** of `SingleD`. **Each run has both defects and the
  unit system decides which one matters.**
- ⚖️ **This refines a B2 sentence rather than overturning it.** B2 said *"exactly one of the two
  defects"*. True on SI (`d2` = 0.00 exactly); on IP both are present and one is 0.1 %. Recorded here
  rather than quietly reworded there. **Corroboration:** `SingleD`'s water share is 40.8 % here and
  38 % in Leg-2's separate campaign.
- 🔴 **Three of four band verdicts change, and all four archetypes end up BELOW their SHEU ranges.**
  2022: SingleD 200 → **115**, OtherDwelling 115 → **100**, MidRise 170 → **108**, HighRise 128 → **78**.
  The published table said one above, one below, two inside. **The two that read "Yes" are among the
  three that move.** With the paper's own ×1.11 apartment renormalisation MidRise returns inside;
  HighRise does not.
- 🔴🔴 **A second, unlooked-for defect in the writing set.** `2J_full_manuscript.md` is on a
  **superseded campaign** — the one the 2026-07-11 two-panel re-simulation replaced — while
  `readySubmission.md` is current. **Same mtime, so the staleness is invisible from the filesystem;**
  it was found only by reproducing each table from its own data.

**Files changed** (predecessors archived to `writing/fullSet/archive/*.2026-08-06_pre_V4-B4.md`):
`readySubmission.md` Table 5 + §5.2 + notes; `2J_full_manuscript.md` Table 5 + a note naming **both**
its errors.

⚖️ **What was deliberately NOT done.** §5.2's three-paragraph defence of the over-band reading is now
defending an artefact and was replaced; the replacement states only what is measured plus one
interpretive sentence — that a current-code NECB-2017 / NBC-9.36 envelope sitting below survey
averages drawn from the **existing** stock is the expected direction. **That sentence is an authorial
claim, not a measurement, and is flagged for the user's sign-off.** The `.docx` was **not** rewritten:
its runs are split across XML elements and it is an outward-facing file. The "+2.85 % phase
invariance" figure compares two campaigns that are **both** contaminated and is marked **unverified**
rather than left implying it was checked.

🔁 **Reopen triggers.** (1) Any Step-8 re-aggregation **must** be preceded by fixing `calculate_eui()`
itself — pin `ReportName` and make the water guard unit-agnostic — or it will reproduce the defect
faithfully. (2) If `2J_full_manuscript.md` ever becomes the submission vehicle it needs the **campaign**
fix too. (3) If the v1 campaign is recovered, re-derive +2.85 % on corrected values.

---

### V4-C1 — Retail quarantine: one cause, two severities

**Owed decision, small but a scorecard change.** When the retail chain is quarantined, `RW1` is graded
**FAIL** while `RETM` and `RW9` are graded **WARN** — one cause, ~~three lines~~ **five lines**, two
severities. Whatever the right answer is, it is not "both". **Not fixed in v3 deliberately**: changing
it changes the scorecard, and v3 changed no statuses.

#### ✅ DECIDED AND EXECUTED 2026-08-06 — all lines graded **FAIL**

**The decision (user, 2026-08-06).** Align **upward**. One cause, one severity, most severe wins.

🔴 **The item's own premise was wrong, and the error was in the direction that matters.** The plan
said *three* lines. Grepping the guard (`if not self._retail_ok:`) rather than trusting the count
found **four** explicit quarantine records — and a **fifth** that never says the word:

| line | gate | was | now | how it was found |
|---|---|---|---|---|
| `:1011` | `RETM` | warn | **fail** | named in the plan |
| `:1133` | `RW1` | fail | **fail** (unchanged) | named in the plan |
| `:1280` | `RW9` | warn | **fail** | named in the plan |
| `:1762` | `GA-3` | warn | **fail** | 🔴 **not named** — same guard, same message string |
| `:1781` | `GB-3` `[retail]` | warn | **fail** | 🔴🔴 **not named, and does not mention retail** — the loop header blanks the retail columns when the gate fails, so a generic *"no observed data"* warn **is** the quarantine in different wording |

**Grading only the three named lines would have rebuilt the identical defect one line smaller** — one
cause, still two severities. That is the whole content of this finding: *the count in a task
description is a claim about the code, and it was never checked against the code.*

⚖️ **Deliberately narrow at `GB-3`.** Only `ch_name == "retail" and not self._retail_ok` is regraded.
`home` and `work` reaching the same branch is a genuine missing-data warn and keeps its severity.
*"No observed data is always FAIL"* is a **different and larger decision** than the one taken, and it
was not taken here.

🔁 **Reopen trigger.** If a future round finds a **sixth** line carrying this cause, the fix is not to
grade it — it is to replace all five special cases with a single quarantine helper that grades once,
because a defect that regrows twice is a structural problem and not a severity typo.

**Files.** `Leg3_4-split/Step4_docs/3rdJ_04_augmentationGSS_4split_val.py`, md5
`02ae34c8…` → `cd7927c1…`; predecessor archived as
`archive/3rdJ_04_augmentationGSS_4split_val.2026-08-06_pre_V4-C1.py`. Compiles clean.
**Nothing was re-run** — the shipped Step-4 report predates even `RW9` (see `V4-C2`), so no scorecard
artefact on disk changes today. **The severities change; the published report does not yet show it,
and that is stated rather than hidden.**

---

### V4-C2 — `RW9` is in the validator code and not in the shipped Step-4 report — BLOCKED

The person-level retail check built in v3-J1 exists in the code and **fails**. The shipped Step-4
report predates it. Regenerating locally would stamp a cluster artefact `win32`, and ~~the standing rule
is **stay local — do not contact Speed at all**. So this is blocked on an action I am not permitted to
take, which is the correct place for it to sit.~~

#### 🔴 The stated reason was **stale**, so it was checked — and the block **survived** (2026-08-06)

The justification above cites a rule the user **replaced the same morning**: retrieval from Speed is
now allowed. `V4-B2` had just shown that a block phrased as *"the file is on Speed"* can be a
rule-reading rather than a resource. **So the same question was put to this item, on the user's
instruction (*"vérifier sur le Speed, tu peux faire, vas-y"*).** Retrieval only, `ls` and `grep` on
single files:

| checked | result |
|---|---|
| `…/Leg3_4-split/Step4_docs/outputs_step4/sweep/seed_3_raked3_mindwell_actv/` | exists; `step4_validation_report.{txt,html}` dated **Jul 20 11:33–13:45** |
| `grep -c RW9` on Speed's `step4_validation_report.txt` | **0** |
| `grep -c RW9` on Speed's `3rdJ_04_augmentationGSS_4split_val.py` | **0** |

**`RW9` was wired locally on 2026-08-06 and never uploaded**, so Speed's validator cannot contain it
and Speed's report predates it by six weeks. **There is no linux-stamped artefact to fetch.** Closing
this needs the validator uploaded and *run* on the cluster — compute, which the amendment explicitly
did not grant (*"tu ne peux pas utiliser pour des simulations"*), and which I will not infer.

🔴 **This is the result that makes the `V4-B2` check worth having run.** Two items carried the same
stale reason; **one was the rule and one was the resource**, and the only way to tell them apart was
to look. **A block that survives an honest check is a stronger block than one that was never
tested** — and the record now says which kind this is.

**Note added by `V4-C1`:** because this report was never regenerated, today's five severity changes
are **in the code only**. No scorecard artefact on disk shows them.

🔁 **Reopen trigger.** Authorising an `sbatch` validator run on Speed — which is not a simulation
cell — closes `V4-C2` and `V4-C1`'s reporting gap in one job. **That authorisation is the user's and
has not been given.**

Also carried here: the local `3rdJ_04D_train_4split.py` differs from Speed's copy by a comment block.
Comments only; it cannot change a result.

---

### V4-C3 — QC hotel occupancy is Power-BI-locked — BLOCKED

AB occupancy was solved through open OGLA PDFs (2011–2022). QC remains behind a Power-BI front end
with no open equivalent found. This is why hotel is uninjected before 2019 and why `S9-LONG-hotel`
passes vacuously. **Reopen if an open QC source pre-2019 appears.**

#### ✅ 2026-08-06 — the only permitted move was made: the prompt is written

**Decided by the user:** author the deep-research prompt. Deep research is **external** — I do not
search, and I do not verify a citation myself; the deliverable is a prompt file, not an answer.

**Written:** `deepResearch_Resources/V07_qc_hotel_occupancy_pre2019.md`, in the house style
(`Why we are asking` / `What we need` / `Named leads` / `Deliverable`), pointing at
`00_MASTER_BRIEF_V2.md` and `_RESPONSE_TEMPLATE.md`.

Three things in it are deliberate:

1. **The lead most likely to work is named first for a reason** — `donneesquebec.ca` is a **CKAN**
   portal, and CKAN's package-search API is *exactly* how the Alberta series was found. The prompt
   says so, so the external tool does not rediscover our own method.
2. **`NOT FOUND` is defined as a successful answer**, and Section B must list what was checked and
   how. A reusable negative is worth paying for once; it is not worth paying for twice.
3. **CBRE is named only to be excluded.** We have never obtained CBRE data, and a previous round
   mis-tagged the AB source as CBRE. The prompt states outright that a CBRE figure must not be
   reported as retrievable — because **every one of the five deep-research rounds so far contained a
   fabricated number**, and the prompt is the only place to say so in advance.

**Status unchanged: BLOCKED.** Writing the prompt is not finding the data. `S9-LONG-hotel` stays a
vacuous pass and stays labelled one.

🔁 **Reopen trigger.** `RV07` returns with a URL that opens to monthly QC values for any part of
2011–2018 — **verified by opening it, not by its presence in the report.**

---

## 3. What must be true at closure

1. Every owed item is visible in **all three** artefacts — this plan, the manager prompt, and the
   board — and `j4_ledger_check.py` fails if any one of them drops it.
2. **No band value, threshold or rule value moves** except where an owed decision explicitly
   authorises it, and then only with the decision recorded and a reopen trigger written.
3. **No gate is resolved by choosing the rule that passes.** Where a unit or basis change is on the
   table (V4-A1), the sub-verdicts are written down before scoring, and a change that cannot produce
   a FAIL is not adopted.
4. Speed is not contacted. No simulation cell is run.

---

## 4. Decisions taken — 2026-08-06

**Four of the five owed decisions were taken by the user on 2026-08-06.** Each carries its **recorded
reason** and its **written reopen trigger**, per the standing rule. 🔴 **Not one of them moves a band
value, a threshold, a rule value or a gate status by itself.** A1 authorises a scoring unit; A4 does
the scoring, and A4's outcome is bound in advance by §2's pre-registration.

### 4.1 — V4-A1: authorise the per-geometry split *(option c)*

**Reason.** The population is bimodal with a ~~31.07 kWh/m² empty gap and the 180 floor~~ **84.64
kWh/m² empty gap (70.5 % of the band) and the 300 ceiling** inside it, so
neither `all_cells` nor the median describes the data. *(Figures restated 2026-08-06 by `V4-A4`: the
reason was written from the superseded `outputs_step9/`. **The premise is not weakened — the gap is
2.7× larger on the frozen deliverable — but the decision was taken on numbers from the wrong file, and
that is recorded rather than quietly corrected.**)* Of the four options this was the only one that
(i) takes its unit from a design variable fixed before any EUI existed, (ii) had both sub-verdicts
written down before the choice, and (iii) **is predicted to add a FAIL rather than remove one**.

⚖️ **Stated against it, and not resolved by the decision.** An honest geometry classifier is still not
an occupancy gate. **The split does not make `S9-EUI-hotel` informative about this project's subject**
— that limitation (Finding 1) stands and stays in the pipeline document whatever A4 returns.

🔁 **Reopen trigger.** If the executed split does **not** produce at least one hotel FAIL, the split is
reverted, the rule returns to `all_cells` unchanged, and the discrepancy against the written
prediction is logged as a finding.

✅ **EXECUTED 2026-08-06 (`V4-A4`, §2.4).** `Tall` **FAIL** 28/28 over the ceiling, `SuperTall` **PASS**
28/28 in band. **The trigger did not fire** — a hotel FAIL survives, so the split stands and does not
clear a blocker. 🔴 **Both written sub-verdicts were nevertheless wrong, and inverted**, for the same
reason as the reason above: they were computed on the superseded artefact. **Logged as a finding, per
the rule, rather than treated as a correction to the prediction.**

### ~~4.2 — V4-B1: per-object resize is the instrument~~ — 🔴 **WITHDRAWN: decided and executed on 2026-08-05**

~~**Reason.** Every heater except `LAUNDRY` has slope exactly 0.000 in both arms; `LAUNDRY` is
capacity-pinned at K=1 and K=6 alike. A global K sized 16 objects by the factor that fixes one. The
instrument is wrong even where the number it produced is right.~~

~~🔁 **Reopen trigger.** Revisit if a second object is ever shown to be capacity-pinned — the "one
object" premise is what makes per-object the right unit, and it is a measured claim, not a structural
one.~~

🔴 **This decision was not the user's to take, because it had already been taken — by them, the day
before.** `V2-B4` decided per-object resize on **2026-08-05**; `V2-D10` implemented and ran it the same
evening, locally on win32, and closed D1–D6; the deliverable ships
`Laundry Service Water Use 30.6gpm 180F=8.5`. **The reasoning above is sound and the state attached to
it was false**, including the claim that execution was blocked on compute. Full withdrawal in §2.5.
**Nothing about the deliverable changes; one row leaves the ledger.**

### 4.3 — V4-B2: quantify from local outputs before choosing the disclosure route

**Reason.** 1.706× is a single-cell measurement. Choosing between erratum and re-publication on a
factor rather than on the affected published numbers is deciding without the input.

🔁 **Reopen trigger.** If the local outputs are absent, this becomes BLOCKED **and is reported as
blocked** — a missing input is not a licence to pick the cheapest option.

✅ **EXECUTED 2026-08-06, and the trigger fired as written (§2.6).** The reach was measured — **all 8
published rows, not 4** — and **uniformity was refuted (1.4868–1.7601, 18.4 %)**, so the correction
cannot be done by division. The corrected values need the campaign SQL, which is not on this machine:
**BLOCKED, and reported as blocked.** 🔴 **The decision this served is now better posed than it was:
choosing between an erratum and a re-publication was never about a factor, and it is not about office
alone.**

### ~~4.4 — V4-B3: quantify now, then notify — with an expiry~~ — 🔴 **WITHDRAWN: nothing is owed**

~~**Reason.** The magnitude is the input every disclosure route needs, and it is desk work. But the
recorded risk on this item is that measurement becomes the reason nothing is said, so the decision is
"quantify **then notify**", not "quantify and see".~~

~~🔁 **Reopen trigger / hard stop.** **2026-08-13.** After that date the notification goes out with the
magnitude unmeasured and said to be unmeasured.~~

🔴 **Struck. `V2-A1` had already established, on 2026-08-04, that `B-13` does not reach the submitted
paper** — the transform is in a converter retired 2026-05-31, and `readySubmission.md:231` explicitly
describes the mean-fraction channel that does ship and disambiguates it from the §3.3 maximum. **The
magnitude the deadline was meant to force had also already been measured: 32.55 % of person-hours.**
**The hard stop is cancelled; no notification is owed.** §2.7 and `V4-B3_withdrawal.md`. **This
decision, like §4.2, was put to the user on a false premise and their answer was spent on it.**

### 4.5 — Still owed: V4-C1

Retail quarantine grades one cause at two severities (`RW1` FAIL, `RETM`/`RW9` WARN). Deliberately
held back from v3 because it changes the scorecard. **This is the single remaining 🟣 row.**

### 4.6 — Step 9 closes as **DELIVERED WITH DOCUMENTED LIMITATIONS**, with all three EUI gates still FAIL

**Taken 2026-08-06 on the user's instruction** (*"vas-y avec ton recommendation"*), against the
recommendation as written. **Recorded in the Step-9 master document as `§10. CLOSURE`.**

**The decision.** Step 9 is closed. `S9-EUI-office`, `S9-EUI-retail` and `S9-EUI-hotel` **stay FAIL** —
not converted to WARN, not re-based, not re-scored under a different rule. **No band value, floor or
ceiling moves.** The step's own stated scorecard target (*"0 FAIL"*) is **declared not met**, and that
declaration is the closure rather than a deferral. What changes is **what the gates are claimed to
test**, not their verdicts.

**Reason.** The **uninjected `Default_NECB` control** fails **two of the three** before any occupancy
model is in the building — hotel `Tall` at **304.41 / 315.82** against a 300 ceiling, office at
**81.65–90.21** against a contested 100 floor. A gate no untreated control can pass is not reporting on
the treatment. `V4-A5` then names the hotel mechanism outright: **one DHW load sized per building and
divided by a floor area that halved**, carrying 93.4 % of the separation and moving 0.01 kWh/m² across
all 14 scenarios.

🔴 **The third gate is deliberately not covered by that argument.** The **retail control passes** —
87.21–96.84, all four cells inside [80, 155] — while the scored median is 75.6, below the floor. So
`S9-EUI-retail` fails on cells the model produced, and it is closed as the model's failure, not the
band's. **An argument that acquitted all three at once would be a blanket, not evidence**, and the
control was read for each channel separately for exactly that reason.

⚖️ **Stated against it.** Closing a step with three declared failures is a worse-looking scorecard than
any of the alternatives, and every alternative was available: re-base hotel EUI on rooms, adopt the
office band's lower published floor (the same source gives 100, 80–140 and 85–115), or switch hotel to
the median rule, which **passes on this same data**. **Each of them changes the criterion until the
result changes.** A basis change that turns a FAIL into a WARN is a band change wearing a different hat
(R1, 2026-07-21). **Three failures with a named cause are a stronger result than a green scorecard
whose criterion was chosen after the fact.**

🔁 **Reopen trigger.** Four, written in `§10` of the Step-9 document: a third hotel geometry; a
per-floor-area DHW resize (with its prediction — `Tall` falls ~79 kWh/m² — written down in advance); a
**sourced** office floor (an unsourced one does not reopen it); and any proposal to move a band on this
evidence, which `§10` exists to refuse.

### 4.7 — v5 is opened as a **tooling round**, and is meant to produce no findings

**Taken 2026-08-06 on the user's instruction.** Plan: `improvements/v5/3rdJ_L3_v5_tooling.md`.

v4 made exactly two process errors — the wrong input directory, and opening two items that were
already closed — and both were caught by hand, late. v5 turns each into a check that fails by itself:
`f1_frozen_input_check.py` (4 checks) and `f2_no_reopen_check.py` (4 checks). **Both are seen failing
on static fixtures reproducing the real historical errors, and both run clean on the live v4 round.**

🔴 **F1 found a real line in the working tree on its first execution** — and **C1 passed while C2
failed**, which is why the two are separate checks: the wrong directory reached the script as a
`join()` component, not as a path literal. 🔴 **F2's first draft chained D1 and D2 with `elif`**, so
D2 could only be reached when D1 passed — **the same defect `V2-G5`'s falsifier had**, reappearing
within an hour of the rule being written down. They are independent now, and the fixture carries a
D2-only case to prove it.

**This round adds no result and moves no number.** The reason it is a round rather than a note: v4
exists because open items were prose rather than tasks, and leaving v4's own lesson as prose repeats
the defect one level up.

---

## Progress Log

### 2026-08-06 (late) — **worked to the end: A4 executed, B2 measured, B1 and B3 withdrawn, one finding retracted**

**Everything not blocked was taken to a terminal state in one pass. No gate moved, no band moved, no
simulation ran, the cluster was not contacted, and `Leg2_2-split/` was read-only throughout.**

#### 🔴🔴 The one that matters: the wrong input file, and it had been feeding four items

`V4-A4` scored the split and **both of its pre-registered sub-verdicts came out inverted.** Running the
identical scoring on `Step9_docs/outputs_step9/` **reproduces both predictions exactly**, which locates
the fault precisely: **A2, A3, A4 and the §4.1 decision reason were all computed on a 2026-07-31
directory that is not the frozen deliverable** (`outputs_step9_deliverable/`, 2026-08-06 00:05, named
in `V2-G1_FROZEN_DELIVERABLE.md`). Office and retail differ by ~0.1 %; **hotel inverts**.

⚠️ **`V4-A2`'s Finding 2 is therefore RETRACTED, and the master document was right all along.** It
said the hotel failures are *"over the ceiling, all `Tall`, zero `SuperTall`"* — which the deliverable
confirms (`verdict_asmodelled`: `Tall` 28 FAIL / `SuperTall` 28 PASS, range 203.33–318.42). **I struck
three correct passages and replaced them with numbers imported from a neighbouring artefact — the exact
defect the correction was accusing the document of.** Only the count was genuinely wrong: **28, not
21** (21 matches neither basis; GFA-share gives 14, and its provenance is unresolved).
🔴 **And the inversion was already written down** in the v2 closure prompt §V2-E5: *"the failing end
inverted while the count held still."* **Both artefacts report "28 of 56" — the count holding still is
what made the substitution invisible.** Sites corrected additively in the pipeline document (×4), the
overview (×2), this plan and the manager prompt.

#### The findings survive the correction, and one is much larger

`S9-EUI-hotel`'s bimodality is **worse** on the canonical data: clusters `SuperTall` **203.33–218.22**
and `Tall` **302.86–318.42**, empty gap **84.64 = 70.5 % of the band's own width**, **the 300 ceiling
inside it**, pooled median **260.54** describing no building. Injection moves each cell by
**−1.55 to +2.60 (≤1.00 %)**, and 🔴 **both `Tall` controls are already over the ceiling and both
`SuperTall` controls already in band before any occupancy is injected.** ⚖️ The split fixes
*attribution*; **it does not make this gate informative about occupancy**, and that sentence stays.

#### 🔴 Two of the four decisions taken this evening were never open

| | it was | closed on | where it says so |
|---|---|---|---|
| **`V4-B1`** | decided **and executed** | **2026-08-05** | `V2-B4` decided per-object resize; `V2-D10` implemented and ran it locally, D1–D6 closed; deliverable ships `…30.6gpm 180F=8.5`. Plan rows 372 and 393 |
| **`V4-B3`** | falsified and withdrawn | **2026-08-04** | `V2-A1`: *"B-13 does NOT reach the submitted paper. No erratum is owed."* Terminal-status row at line 1269 |

**Both were written into v4 from prose — memory, the audit document, superseded prompts — and neither
was checked against the v2 plan before being called open.** Worse, **both were put to the user as
decisions**, so their attention was spent on questions that already had answers. **v4 existed because
open items were prose and not tasks; it then turned prose into two tasks that were already finished.**
The v4 claim *"B1's execution is BLOCKED on compute and the stay-local rule"* was false — it had
already run **locally, on this machine, without the cluster**. **The 2026-08-13 hard stop is
cancelled.**

**Rule adopted (a `j4_ledger_check` candidate, not a resolution):** *a new round may not open an item
naming a `B-*`/`C-*`/`G-*` audit finding without quoting that finding's terminal-status row from the
v2 plan.* The table exists and was one grep away.

#### `V4-B2` — the reach measured, and it is bigger than the finding

`calculate_eui()` is called on **both** aggregator branches (`agg.py:438` residential, `:481` office),
so **all eight published Leg-2 EUI rows are contaminated, not four.** 🔴 **Uniformity refuted:** across
the 12 Leg-2 SQL on this machine the factor runs **1.4868–1.7601, an 18.4 % spread**, and it tracks the
**household** rather than the arm — it is a peak-demand-to-annual-energy ratio. **`172.7 ÷ 1.706` is
not a valid correction.** Two published PASSes (`OtherDwelling`, `HighRise`) fall below their floors
under **every** factor in that range; the sole WARN (`SingleD`) can move to PASS **or** to a
below-floor miss — *the same inversion shape as the hotel gate*. **BLOCKED on the campaign SQL and
reported as blocked**, per this item's own pre-registered guard: `outputs_step8/office/` is empty,
`office_idfs_v242/` holds 4 IDFs and no results, and the cluster was not contacted.

#### What did not move

**All three `S9-EUI-*` still FAIL.** Every band value byte-identical. `step9_gates.json` untouched in
both directories. `Leg2_2-split/` and the 2J manuscript were read, never written. **Four states moved,
two rows left the ledger, and zero gates moved.**

~~**Remaining: `V4-C1` (the only thing owed by the user — its premise was re-verified against v3 §J,
which records it as deliberately not fixed), `V4-B2`'s corrected numbers (blocked on compute), `V4-C2`
(blocked on the stay-local rule), `V4-C3` (blocked on QC data access).**~~

🔴 **CORRECTED same day:** *"blocked on compute"* was wrong twice over. The block was **a reading of the
standing rule, not a resource** — the user amended it hours later (*retrieval yes, simulation no*) and
all 652 runs were fetched with `scp` the same evening. **Remaining: `V4-C1` only** (owed by the user),
plus `V4-C2` / `V4-C3`.

---

### 2026-08-06 (late) — **V4-B2 CLOSED end to end: 652 published runs re-read, a pre-registered prediction FAILED, and a SECOND defect found**

**Retrieval only. `scp` → local `sqlite3` → delete → next, peak local disk one file. No `sbatch`, no
`srun`, no login-node `python`, no simulation cell.** Write-ups: `V4-B2_corrected.md` (office),
**`V4-B2_corrected_resid.md`** (residential), `V4-B2_defect_reach.md` §8 (the second defect).

**652 of 652 runs retrieved** — 252 office (the complete published population, 3 first-pass `scp`
failures all recovered on retry) and 400 residential (100 per archetype, a **pre-registered** sample of
2 100 each, zero failures). **Both halves passed their reproduce-the-published-population guard before
any corrected number was read.**

| published row | n re-read | published | **corrected** | band | published | **corrected** |
|---|--:|--:|--:|---|---|---|
| office ×4 | 252 | 172.7 / .6 / .5 / .7 | **106.56 / .66 / .71 / .56** | [100, 200] | IN | **IN** |
| `MidRise` | 100 | 177.5 | **128.21** | [111.1, 216.7] | IN | **IN** |
| `HighRise` | 100 | 143.0 | **101.23** | [113.9, 147.2] | IN | 🔴 **BELOW** |
| `OtherDwelling` | 100 | 140.0 | **124.98** | [136.1, 186.1] | IN | 🔴 **BELOW** |
| `SingleD` | 100 | 211.7 | **130.57** | [130.6, 186.1] | **ABOVE** | 🔴 **not ABOVE; undetermined** |

**🔴 THREE of the eight published rows change verdict, and one of them is the sole published WARN.**
`G2r` WARNs because `SingleD` overshoots the SHEU ceiling; corrected it sits at the **bottom** of the
band. **The condition the WARN describes is not there** — the same inversion shape as `S9-EUI-hotel`.
⚠️ `SingleD` misses its floor by **0.03** inside an interval **8.3 wide**: **UNDETERMINED between BELOW
and IN**, and recorded that way rather than rounded to BELOW.

**🔴 P1 was pre-registered and FAILED.** It named `HighRise` **and** `OtherDwelling` as falling below
their floors under the defect-1 correction. `HighRise` did; **`OtherDwelling` gave 139.88, IN.**
`V4-B2_defect_reach.md` §3's *"BELOW, either way"* is **withdrawn for that row**, and §3's *"IN, or
BELOW"* for `SingleD` was **neither** — it did not move.

**🔴🔴 Chasing the failure found a SECOND defect in the same function.** The water guard
`if 'm3' in str(units): continue` (`plotting.py:319`) is **SI-only**, so IP water in `gal`/`gal/min`
is summed as kWh — **38.08 % of published `SingleD`, 10.66 % of `OtherDwelling`.** The two defects are
**complementary and every run has exactly one**: SI runs report demand in `W` (defect 1 fires), IP runs
in `kBtuh` with water in `gal` (defect 2 fires). **§1's "all 8 rows contaminated" is confirmed; its
explanation of *how* covered half of them.**

**🔴 §3's direction was right for `OtherDwelling`. P1 still failed and stays failed.** §3 reached BELOW
by dividing by 1.49–1.76; the row's real defect-1 factor is **1.002**, and it falls because a tenth of
it is water. **Right verdict, wrong quantity — a prediction is not confirmed by a mechanism discovered
while investigating its failure.** New rule: *a correction is only as pre-registered as its definition;
naming the direction is not enough.*

**✅ The vacuity guard fired and was obeyed.** `b2_resid_two_defects.py` prints every `(ReportName,
Units)` pair before any total and refuses to vouch for a corrected number while an unclassified unit
exists. **It refused on its first run, over `W` and `kBtuh`.** After classifying them as power, two
structural claims are **checked rather than assumed**: no power unit under the annual report, and no
energy unit outside it.

**🟢 Leg-3 is immune to both defects — verified, not asserted.** `3rdJ_08E_aggregate_4split.py:554`
builds EUI from hourly `Electricity:Facility` / `NaturalGas:Facility` **meters** in Joules (`:343`),
never from `TabularDataWithStrings`. **No Leg-3 number is touched.**

#### What did not move

**All three `S9-EUI-*` still FAIL. Every band value byte-identical. `step9_gates.json` untouched in
both directories. Nothing in `Leg2_2-split/` or the 2J manuscript was written to** — 652 files were
read and deleted. **`V4-B2` closes with one item moved and zero gates moved.**

**Reopen trigger:** `SingleD` resampled at larger n until its interval clears the 130.6 floor either
way; or any run whose unit inventory contains an unclassified unit; or a sample writing a power unit
under the annual report. Full text: `V4-B2_corrected_resid.md` §7.

**Remaining after this: `V4-C1` (owed by the user), `V4-C2`, `V4-C3`.**

---

### 2026-08-06 (evening) — **the last three items answered, and a NEW one that outweighs them: the 2J manuscript's own EUI table is wrong in every cell**

The user answered all three remaining items in one turn and corrected a premise I had been carrying:
**the 2J paper is not submitted.** My record said it was. That correction is what opened `V4-B4`.

**`V4-C1` — decided (all lines FAIL) and executed.** 🔴 **The item's own premise was wrong.** The plan
said *three* lines share the retail quarantine. Grepping the guard rather than trusting the count
found **four** explicit records — and a **fifth** that never mentions retail: when the presence gate
fails, the retail columns are blanked, so `GB-3`'s generic *"no observed data"* warn **is** the
quarantine in different wording. **Grading only the three named lines would have rebuilt the identical
defect one line smaller.** All five now FAIL; the `GB-3` change is deliberately narrow (retail only —
*"no observed data is always FAIL"* is a larger decision and was not taken). Validator md5
`02ae34c8…` → `cd7927c1…`, predecessor archived, compiles clean.

**`V4-C2` — checked under the amended Speed rule, and the block SURVIVED.** Its stated reason cited a
rule the user replaced the same morning, so it was re-tested exactly as `V4-B2` was. Speed's
`step4_validation_report.txt` is dated **Jul 20** and `grep -c RW9` returns **0** — on the report *and*
on Speed's copy of the validator. `RW9` was wired locally on 08-06 and never uploaded, so **there is
no linux-stamped artefact to fetch.** 🔴 **Two items carried the same stale reason; one was the rule
and one was the resource, and only looking could tell them apart.** A block that survives an honest
check is stronger than one never tested.

**`V4-C3` — the only permitted move made.** `deepResearch_Resources/V07_qc_hotel_occupancy_pre2019.md`
written. Status stays **BLOCKED** — writing the prompt is not finding the data.

**🔴🔴 `V4-B4` — opened and closed the same night, and it is the round's largest result.**
**6,000 of 6,000 published runs recomputed, zero guard failures**, after the raw outputs turned out to
be on this machine rather than the cluster — so a planned 400-run sample became a census. The
corrected electricity totals were then checked against the **hourly meter stream**, a path the defect
cannot reach: **max disagreement 0.067 %.**

- **A pre-registered prediction FAILED (Q4).** I predicted a uniformly-SI campaign; it is **3,000 SI /
  3,000 IP, split by archetype.**
- **`published = corrected + d1 + d2` exactly** — reconstruction error **0.0005 kWh/m²**. The unit
  system decides *which* defect matters, through magnitude: `W` is large so the demand double-count
  carries 34–37 % on SI runs; `kBtuh` is 3.4× smaller so it carries 0.1 % on IP runs, where `gal`
  water carries **40.8 %** of `SingleD` instead.
- **Three of four band verdicts change; all four archetypes end below their SHEU ranges.**
  2022: 200 → **115**, 115 → **100**, 170 → **108**, 128 → **78**.
- 🔴 **`2J_full_manuscript.md` was ALSO on a superseded campaign** — same mtime as the current file, so
  invisible except by reproducing each table from its own data.

**Both manuscripts corrected, predecessors archived. The `.docx` was not touched** (fragile XML runs,
outward-facing). **No band moved, no gate moved, no cell was run, nothing under `Leg2_2-split/` was
written to.**

**Remaining: nothing owed by the user. `V4-C2` and `V4-C3` remain blocked, both with the reason
re-verified today rather than inherited.**

---

### 2026-08-06 — v4 opened

Opened in response to the user's question *"où sont les tâches ouvertes que tu as définies avant ?"*
The answer was that they existed only as prose. Ten items are now rows with states; five are owed
decisions; `j4_ledger_check.py` reads the same three artefacts as its v3 predecessor and is **live
again** because there is now something owed for it to lose.

**Nothing has been worked.** This entry records the ledger's creation, not progress on it.

---

### §1 — V4-A2 and V4-A3 CLOSED, and the desk work turned up more than it was sent for

**Same day. No simulation, no re-scoring, no gate, band or rule touched.** Everything below is derived
from `outputs_step9/step9_eui_by_channel.csv`, comparing each `building × city` group against **its
own uninjected `Default_NECB` cell** — geometry, envelope, climate and plant held fixed, only the
schedules varying. **Deliverable landed as limitation `L8`** in the master pipeline document.

| channel | uninjected control | injection then does | reading |
|---|---|---|---|
| office | **81.70–90.33**, all 4 **below** the 100 floor | a further **−15.21 to −18.48** | ~half and half |
| retail | **87.60–97.05**, all 4 **in** [80,155] | **−19.65 to −23.94** | **entirely ours** |
| hotel | 149.36/160.65 `SuperTall` · 195.41/206.79 `Tall` | **+0.06 to +1.45 (≤0.70 %)** | not occupancy |

**V4-A2 — office.** Strongest available form: the **highest office value in all 56 cells and all 14
scenarios is 90.33**, still **9.67 % under the floor**, and the untreated control is already below it.
**The band is unreachable by this configuration, not merely missed.**
⚠️ **A number I had been repeating is wrong.** *"~15 of the 22 kWh/m² predates the injection"* is an
**arm-A** figure, not Step 9's. On the shipped artefact the total gap is **26–37** and the split is
closer to **half and half**. It was in my notes, in the manager prompt and on the board. **Corrected in
all three.** *A number carried across arms without its arm label* is exactly how the defect below
happened.

**V4-A3 — retail.** The uninjected control **passes in all four groups**, so nothing predates the
injection; the injection removes **20–24 kWh/m² (≈21–25 %)**. The 12 passing cells are exactly the **4
control cells + the 8 Montréal cells of the four observed eras** — every Calgary cell, every 2030
bundle and every sensitivity cell fails. **Survivors clear the floor by 0.57 %–3.3 %**, the thinnest
margin on the scorecard. **Gate stays FAIL, band untouched.**

#### 🔴 Finding 1 — `S9-EUI-hotel` cannot see occupancy, and a band boundary lies where no building exists

🔴 **CORRECTED 2026-08-06 by `V4-A4`. The finding holds and is substantially larger; every number in
the original statement was from the wrong artefact and the failing end is the opposite one.**

| | ~~as first written (`outputs_step9/`, 2026-07-31)~~ | **corrected (frozen deliverable)** |
|---|---|---|
| clusters | ~~SuperTall 147.87–162.76 · Tall 193.83–209.43~~ | **SuperTall 203.33–218.22 · Tall 302.86–318.42** |
| largest empty gap | ~~31.07 = 25.9 % of the band~~ | **84.64 = 70.5 % of the band** |
| boundary inside the gap | ~~the 180 **floor**~~ | **the 300 **ceiling** |
| median describing no building | ~~178.29~~ | **260.54** |
| injection moves the channel | ~~≤1.45 (≤0.70 %)~~ | **−1.55 to +2.60 (≤1.00 %)** |
| which geometry fails | ~~SuperTall, below the floor~~ | **Tall, above the ceiling** |

The verdict is decided entirely by geometry, and 🔴 **by the untreated control**: both `Tall`
`Default_NECB` cells are **already over the 300 ceiling** (304.41 / 315.82) and both `SuperTall`
controls **already in band** (204.83 / 216.06), before any occupancy is injected. **The gate returns
the same answer with and without the occupancy model — a blocking gate that is vacuous with respect to
the thing it is named for.**

#### ~~🔴 Finding 2 — the master document describes the hotel failures INVERTED, in three places~~ — 🔴🔴 **RETRACTED**

~~`step9_gates.json`: *"28/56 cells inside [180–300]; median 178.3, **range 147.9–209.4**"* against a
ceiling of **300** — **not one cell is over the ceiling.** The master document says, three times, that
the gate **"FAILs on 21 of 56 cells, all over the ceiling, all `Tall`, zero `SuperTall`."**
**Opposite end of the band, opposite geometry, different count.** Those are **K=6 DHW-resize arm**
numbers, printed under Step 9's heading with no arm label.~~

~~🔴 **And a RESOLVED open decision rests on it.** Open decision 6 (hotel amenity-zone modulation)
argues from *"the failures are `Tall`-only with zero `SuperTall`"* — **the exact inverse of the
artefact.** **Its conclusion survives** and is in fact strengthened: the failure is on the geometry
axis either way, and Finding 1 shows amenity modulation could not reach it (≤0.70 %). **But it was
reached through an inverted reading**, and that is recorded rather than quietly re-justified.~~

🔴🔴 **RETRACTION, same day, by `V4-A4`. The document was right and this finding was wrong.** It read
`Step9_docs/outputs_step9/step9_gates.json` (**2026-07-31 11:42**), a sibling of the frozen deliverable
`outputs_step9_deliverable/` (**2026-08-06 00:05**). In the deliverable the hotel cells run
**203.33–318.42** with **28 above the 300 ceiling and 0 below the 180 floor**, and
`verdict_asmodelled` tallies **`Tall` 28 FAIL / `SuperTall` 28 PASS**. **Over the ceiling, `Tall`-only,
zero `SuperTall` — exactly what the document said.**

**One part of the original text is genuinely wrong: the count.** It is **28**, not 21 — and 21 matches
neither basis (GFA-share gives 14), so it is not a basis mix-up and its provenance is unresolved.

⚠️ **Open decision 6 is restored to its original footing.** It did not argue from an inverted clause;
it argued from the deliverable. Its conclusion stands on the evidence it actually cited, and Finding 1
as corrected supports it more strongly (≤1.00 % against an 84.64 gap).

🔴 **The class was right and the instance was mine.** Third instance in three days of a number imported
from a neighbouring artefact without its label — **committed inside the correction that named the
class.** And the reason it was invisible: **both artefacts report "28 of 56" for this gate.** The count
held still while the failing end inverted, which `V2-E5` had already written down on 2026-08-05. Sites
corrected additively in `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` (~422, ~574, ~649, ~573),
`…_Overview.md` (~270, ~274), this plan and the manager prompt.
**`3rdJ_09_bench_doc_sync_check.py` still PASSes** — as it must: it compares band *values*, and no
value moved. **It cannot see a failure-direction claim at all.**

**Status: V4-A2 DONE · V4-A3 DONE.** Ledger 10 → **2 done · 5 decision · 3 blocked**.

---

### §2 — four of the five decisions TAKEN, same evening

The user was presented with the four decisions that have consequences outside this round, each with
its options and the argument against the recommended one, and took all four. **`V4-C1` was held back
by me, not by the user** — it only relabels a scorecard severity, and putting five questions where
four have external consequences dilutes the four.

| id | taken | what it authorises | what it does **not** do |
|---|---|---|---|
| **V4-A1** | per-geometry split *(option c)* | the scoring unit for `S9-EUI-*` | **does not score anything** — that is A4 |
| **V4-B1** | per-object resize is the instrument | retires the global K as the sizing basis | **changes no IDF sizing value; nothing runs** |
| **V4-B2** | quantify locally, then choose | a measurement of the 1.706× defect's reach | **does not choose erratum vs re-publication** |
| **V4-B3** | quantify now, **then notify** | the magnitude, plus a drafted description | **I send nothing** — notification is the user's act |

🔴 **Three states changed and no gate moved.** A1 DECISION→DECIDED, A4 BLOCKED→READY, B2/B3
DECISION→READY. `S9-EUI-office`, `S9-EUI-retail` and `S9-EUI-hotel` all remain **FAIL**; every band
value is byte-identical; `step9_gates.json` and `step9_eui_by_channel.csv` are untouched.

**Two things were written down at decision time rather than after it**, because both are the kind of
claim that is worthless once the answer is known:
1. **A4's predicted verdicts** — `Tall` PASS, `SuperTall` FAIL — were already in §2.1 before the
   decision, and §2.4 now binds A4 to them: **a disagreement is a finding, not a correction.**
2. **B3's expiry, 2026-08-13.** The recommendation "measure first" was on record *as expiring* and had
   no date. It has one now.

⚠️ **The honest limitation of taking A1 at all:** the split answers *which unit*, and Finding 1 says
the gate is blind to occupancy **in every unit**. **The decision improves the gate's attribution
without making it informative about this project's subject**, and that is stated in §4.1 against
itself rather than left for a reader to notice.

**Status after §2: 2 done · 1 decided · 3 ready · 1 decision (V4-C1) · 3 blocked.**
