# 3J Leg-3 — manager handoff, 2026-08-06 (**v4 CLOSED** — 7 done · **2 withdrawn as never-open** · **0 owed** · 2 blocked)

> 🔴🔴 **READ THIS BEFORE ANYTHING ELSE — the 2J manuscript's EUI table is wrong in every cell, and
> the paper is NOT submitted, so it can still be fixed.**
>
> You told me tonight: *"ce publication pas soumit, donc nous pouvons changer ce que chose nous
> voulons."* My record said the paper **was** submitted. That correction opened a new item, **`V4-B4`**,
> which is now the largest result of the round.
>
> **6,000 of 6,000 published runs recomputed, zero guard failures.** 2022 values:
> SingleDetached **200 → 115**, OtherDwelling **115 → 100**, MidRise **170 → 108**, HighRise **128 → 78**
> kWh/m². **Three of the four SHEU band verdicts change**, including **both** archetypes the paper
> currently reports as comfortably inside their bands. Corrected, **all four sit below** their ranges.
>
> **Two manuscripts are corrected and their predecessors archived.** One thing needs your sign-off and
> one needs your decision:
> 1. **Sign-off:** §5.2's old defence of the over-band reading was defending an artefact and had to go.
>    Its replacement adds **one interpretive sentence** — that a current-code NECB-2017 / NBC-9.36
>    envelope should sit *below* survey averages drawn from the **existing** stock. That is an
>    authorial claim, not a measurement. **Yours to keep or cut.**
> 2. **Decision:** `writing/sharingCHV/2ndOcc_Journal.docx` still carries the old table (as "Table 4").
>    **I did not rewrite it** — its text runs are split across XML elements and it is the copy you
>    share. Regenerating it from the corrected `.md` is the safe route.
>
> 🔴 Also found, and nobody was looking for it: **`2J_full_manuscript.md` was on a superseded campaign**
> — the one the 2026-07-11 two-panel re-simulation replaced. **Same mtime as the current file**, so the
> staleness was invisible except by reproducing each table from its own data. It was wrong on **two**
> counts, and only one of them was the defect.

> 🔴🔴 **Read §0.5 first. Three things in this round were wrong, and all three were found by executing
> it rather than by re-reading it.** A2/A3/A4 were computed on the **wrong Step-9 directory**;
> `V4-A2`'s "the document is inverted" finding is **retracted** because the document was right; and
> **two of the four decisions taken on 2026-08-06 were about items v2 had already closed.**

---

## 0.1 🟢 Later the same day — you changed the Speed rule, and it unblocked the one real blocker

> **Your words:** *"tu peux obtenir ce que choses tu veux sur le speed, mais tu ne peux pas utiliser
> pour des simulations."* **Retrieval yes. Compute no.**

**Consequence, acted on immediately:** *"blocked because the file is on Speed"* **is no longer a valid
status**, and `V4-B2` was the item it had been written on. The Leg-2 campaign `eplusout.sql` were
copied off one at a time with `scp`, read locally with `sqlite3`, and deleted before the next — **peak
local disk one file. No `sbatch`, no `srun`, no `python` on the login node, no simulation.**

⚠️ **One operational lesson, learned the hard way:** a second retrieval started in parallel made Speed
refuse the connection (`scp rc=255`) and three runs failed. **One stream at a time**, and a failed fetch
must not be recorded as done or the resume silently drops it. **All three were retrieved on the retry;
252 of 252 are in, nothing is estimated.**

### 🟢 The office result, and it is the opposite of the alarm

| | published | **corrected** | verdict |
|---|--:|--:|---|
| office all (n = 252) | 172.7 | **106.56** | IN → **IN** |
| Knowledge / Public / Sales (n = 84 each) | 172.6 / 172.5 / 172.7 | **106.66 / 106.71 / 106.56** | IN → **IN** |

**The guard passed first:** Step-9's median arithmetic on the *shipped* column returns
172.66 / 172.62 / 172.54 / 172.72 — the published table, so this is the published population.

1. 🟢 **No office verdict moves.** `V4-B2_defect_reach.md` said *"depends on the factor"* and could not
   choose. **Measured, they stay in.**
2. 🔴 **Uniformity refuted harder: 1.5182 – 1.9075, a 25.6 % spread** — running *past* the top of the
   residential range. `172.7 ÷ 1.706 = 101.2`; the measured answer is **106.56**. The shortcut gets the
   right verdict for the wrong reason and had no way to know it.
3. 🔴 **The mechanism is measured, not inferred.** The factor is flat across the **7 occupancy
   scenarios** (0.4 %) and swings **17.6 %** across the **6 climate zones**. **It is a building-and-
   weather quantity; occupancy does not touch it.**
4. 🔴 **The median passes and a fifth of the population does not** — 50 of 252 runs fall below the 100
   floor. Under Leg-3's `all_cells` rule this would fail; Leg-2 scored the median. **Reported because it
   is true, not because it changes anything.**
5. 🔴 **An old puzzle is closed and one candidate is dead.** The three subtype medians were
   suspiciously tight (0.18). Corrected they are **tighter, 0.144** — **the defect was not compressing
   them.** The three office occupancy profiles genuinely produce near-identical annual EUI.

### 🔴🔴 The residential result, and it is NOT the opposite of the alarm — it is worse

**400 more runs retrieved the same evening (100 per archetype, a sample pre-registered before the first
file was fetched, from populations of 2 100). 652 of 652 runs re-read in total. Zero failures.**

| published row | published | **corrected** | 95 % interval | band | verdict |
|---|--:|--:|---|---|---|
| `MidRise` | 177.5 IN | **128.21** | 125.05 – 131.18 | [111.1, 216.7] | **IN** |
| `HighRise` | 143.0 IN | **101.23** | 99.38 – 104.77 | [113.9, 147.2] | 🔴 **BELOW** |
| `OtherDwelling` | 140.0 IN | **124.98** | 121.56 – 130.42 | [136.1, 186.1] | 🔴 **BELOW** |
| `SingleD` | 211.7 **ABOVE** | **130.57** | 126.60 – 134.86 | [130.6, 186.1] | 🔴 **not ABOVE; undetermined** |

**The guard passed first:** shipped sample medians reproduce the published table on all four
(worst error **+1.72 %**), so this is the published population.

1. 🔴🔴 **THREE of the eight published rows change verdict, and one is the sole published WARN.** `G2r`
   WARNs because `SingleD` overshoots the SHEU ceiling. **Corrected, it sits at the bottom of the band
   — the condition the WARN describes is not there.** Same inversion shape as `S9-EUI-hotel`.
2. ⚠️ **`SingleD` is UNDETERMINED, not BELOW.** It misses the floor by **0.03** inside an interval
   **8.3 wide**. What *is* settled: **it is no longer ABOVE.** Recorded that way, not rounded.
3. 🔴 **A pre-registered prediction FAILED.** `P1` named `HighRise` **and** `OtherDwelling` as falling
   below their floors under the correction as defined at the time. `HighRise` did.
   **`OtherDwelling` gave 139.88 — IN.** Recorded as failed, not as a half-success.
4. 🔴🔴 **Chasing that failure found a SECOND defect in the same function.** The water guard
   `if 'm3' in str(units)` is **SI-only**, so IP water in `gal`/`gal/min` is summed as kWh —
   **38.08 % of published `SingleD`, 10.66 % of `OtherDwelling`.** The two defects are
   **complementary: every published run has exactly one of them**, decided by whether EnergyPlus wrote
   the run in SI or IP. Confirmed on one probe of each, both factors reproduced arithmetically.
5. 🔴 **`V4-B2_defect_reach.md` §2's 18.4 % factor spread was measured on 12 files that are all SI.**
   The real residential range is **1.0005 – 1.7541, 75.3 %**, separating by unit system.
   **The mechanism survived; the range did not.** Reported as separation with a named cause, **never as
   "bimodality"** — the same rule `V4-A5` established.
6. 🔴 **§3's *direction* was right for `OtherDwelling` and P1 still failed.** §3 got BELOW by dividing
   by 1.49–1.76; that row's real factor is **1.002** and it falls because a tenth of it is water.
   **Right verdict, wrong quantity.** New rule: *a correction is only as pre-registered as its
   definition — naming the direction is not enough.*
7. ✅ **The vacuity guard fired and was obeyed.** The script prints every `(ReportName, Units)` pair
   before any total and **refused to vouch for its own output on the first run**, over `W` and `kBtuh`.
   After classifying them, two structural claims are now **checked**: no power unit under the annual
   report, no energy unit outside it.
8. 🟢 **Leg-3 is immune to both defects — verified against the code path**, not asserted.
   `3rdJ_08E_aggregate_4split.py:554` builds EUI from hourly meters in Joules, never from
   `TabularDataWithStrings`. **No Leg-3 number moves.**

🟢 **`V4-B2` is now CLOSED end to end. Zero gates moved, zero bands moved, nothing in `Leg2_2-split/`
or the 2J manuscript written to** — 652 files were fetched, read, and deleted.

### And four other things were settled on your instruction

| | what you asked | what was done |
|---|---|---|
| **1** | *"d'accord, ajoute"* — write down the problem the submitted paper must disclose | **`V4-B2_corrected.md` §0, and it is now COMPLETE** — all 8 rows, **both** defects, both scoring populations, with `SingleD`'s undetermined verdict stated as undetermined. The office-only draft is struck through and kept above it. **It does not choose erratum vs re-publication — that is still yours** |
| **2** | *"vas-y"* — get the Leg-2 SQL and compute the corrected numbers | **652 of 652 published runs re-read** (252 office + 400 pre-registered residential). Both halves above. **Retrieval only — no `sbatch`, no `srun`, no login-node `python`, no simulation** |
| **3 + 4** | *"vas-y avec ton recommendation"* — what the hotel gate is failing on, and how to word it | **`V4-A5`**: **`dhw` alone carries 93.4 % of the separation** and moves **0.01 kWh/m²** across all 14 scenarios; `Tall` has **exactly half** the hotel floor area and **86 %** of the DHW energy. 🔴 **Written as archetype separation with a named mechanism, NOT as bimodality** — two geometries cannot distinguish a distribution's modes from two archetypes |
| **5** | *"vas-y avec ton recommendation"* — Step 9's end state | **CLOSED as DELIVERED WITH DOCUMENTED LIMITATIONS, with all three `S9-EUI-*` still reading FAIL** (§4.6, and `§10 CLOSURE` in the Step-9 master doc). Not converted to WARN, not re-based, **no band moved** |
| **6** | *"vas-y avec ton recommendation"* — the tooling round | **v5 opened and executed**: `f1_frozen_input_check.py` + `f2_no_reopen_check.py`, 4 checks each, **both seen failing on static fixtures of the real errors**, both clean on live v4. **No finding, by design** |
| **7** | *"oui le papier troisieme"* | the destination is the **third paper**, written like `2J_docs_occ_nTemp/writing/fullSet`. ~~**Starts when v4 closes — which needs `V4-C1`, still yours**~~ ✅ **v4 is closed; `V4-C1` was taken 2026-08-06. The third paper is the next thing to start.** |

🔴 **The one that will look strange on a scorecard: Step 9 ships with three FAILs on purpose.** The
**uninjected control** fails hotel (`Tall` 304.41 / 315.82 vs a 300 ceiling) and office (81.65–90.21 vs
a contested 100 floor) **before any occupancy model is in the building** — a gate no untreated control
can pass is not reporting on the treatment. **The retail control PASSES (87.21–96.84, all inside
[80, 155]), so retail's FAIL is ours and is closed as ours.** Every route to clearing the other two
changes the criterion until the result changes, which is the move R1 forbids.

---

## 0.5 What changed since the version of this prompt you may have read

| id | was | **is now** |
|---|---|---|
| **V4-A4** | READY | ✅ **DONE** — executed. 🔴 **Both pre-registered sub-verdicts inverted**; cause = wrong input file. `SuperTall` **PASS**, `Tall` **FAIL** |
| **V4-A2** Finding 2 | *"the master doc is inverted in 3 places"* | 🔴🔴 **RETRACTED** — the doc was right; only the count (21 → **28**) was wrong |
| **V4-B1** | DECIDED, exec BLOCKED | ⬛ **WITHDRAWN** — decided `V2-B4` **and executed `V2-D10`** on 2026-08-05, locally, without the cluster |
| **V4-B2** | 🟢 **DONE** | **652 of 652 published runs re-read.** Office `172.7 → 106.56`, **verdicts hold**. Residential: **3 of 4 rows leave their bands**, incl. the **sole published WARN inverting**. 🔴 **P1 pre-registered and FALSIFIED**; 🔴🔴 **a SECOND, complementary defect found** (SI-only water guard, `gal` summed as kWh — **38 % of `SingleD`**). Leg-3 verified immune |
| **V4-B3** | READY, hard stop 08-13 | ⬛ **WITHDRAWN** — `V2-A1` falsified B-13 on 2026-08-04. **No erratum owed. Hard stop cancelled** |
| **V4-C1** | ~~🟣 DECISION — the only thing owed by you~~ | ✅ **DECIDED (all FAIL) AND EXECUTED.** 🔴 **The item said three lines; there are FIVE** — `GA-3` shares the guard, and `GB-3`'s *"no observed data"* warn **is** the quarantine without the word. Grading only the three named would have rebuilt the defect one line smaller |
| **V4-C2** | BLOCKED (old Speed rule) | ⚫ **RE-CHECKED under the amended rule — the block SURVIVED.** Speed's report is dated Jul 20 and `grep -c RW9` = **0** on both the report and Speed's validator. **Two items had the same stale reason; one was the rule, one was the resource** |
| **V4-C3** | BLOCKED (data) | ⚫ **still BLOCKED**, prompt `V07_qc_hotel_occupancy_pre2019.md` written for Gemini Antigravity |
| **V4-B4** | *did not exist* | 🔴🔴 **DONE — the 2J manuscript's own table.** 6,000 runs re-read; **3 of 4 band verdicts change**. A pre-registered prediction (Q4) **FAILED** |
| **V4-A5** | *did not exist* | ✅ **DONE** — what `S9-EUI-hotel` is actually failing on: **one DHW load, sized per building, divided by a floor area that halved** |

**Zero gates moved. Zero band values moved. All three `S9-EUI-*` still FAIL. `step9_gates.json` is
untouched in both directories. `Leg2_2-split/` and the 2J manuscript were read, never written.**

### The one that matters — the wrong input file

`V4-A4` scored the authorised split and **both written sub-verdicts came out backwards.** Re-running
the identical scoring on `Step9_docs/outputs_step9/` (**2026-07-31**) **reproduces both predictions
exactly** — so A2, A3, A4 and the §4.1 decision reason were all computed on a directory that **is not
the frozen deliverable** (`outputs_step9_deliverable/`, 2026-08-06 00:05, named in
`V2-G1_FROZEN_DELIVERABLE.md`). **Office and retail move ~0.1 %. Hotel inverts.**

**The finding survives and is larger.** Hotel clusters `SuperTall` **203.33–218.22** / `Tall`
**302.86–318.42**, empty gap **84.64 = 70.5 % of the band**, the **300 ceiling inside it**, median
**260.54** describing no building, injection **≤1.00 %** — and 🔴 **both `Tall` controls are already
over the ceiling before any occupancy is injected.** The split is adopted for hotel, **a FAIL survives
(R1 held)**, and it **buys nothing for office or retail** — which is the reported result.

⚠️ **And I struck three correct passages in the master document.** They said the hotel failures are
*"over the ceiling, all `Tall`, zero `SuperTall`"*; the deliverable confirms exactly that. **The
correction was itself the imported-number defect it was naming.** The count alone was wrong — **28, not
21.** The inversion was already recorded in the **v2 closure prompt §V2-E5** (*"the failing end
inverted while the count held still"*), and **both artefacts say "28 of 56"**, which is why the swap
was invisible.

### 🔴 Two of your four decisions were about closed items

- **`V4-B1`** — `V2-B4` decided per-object resize on **2026-08-05**; **`V2-D10` implemented and ran
  it the same evening, locally on win32**, D1–D6 closed; the deliverable ships
  `Laundry Service Water Use 30.6gpm 180F=8.5`. v4's *"execution BLOCKED on compute"* was false.
- **`V4-B3`** — **`V2-A1`, 2026-08-04: *"B-13 does NOT reach the submitted paper. No erratum is
  owed."*** The transform lives in a converter retired 2026-05-31; `readySubmission.md:231` already
  carries the clause disambiguating it. **The 2026-08-13 hard stop is cancelled.**

**Both were written into v4 from prose without re-reading the v2 plan, and both were put to you as
decisions.** Rule adopted: *a new round may not open an item naming a `B-*`/`C-*`/`G-*` finding without
quoting its terminal-status row from the v2 plan.*

⚠️ **One small live residual from B3, checked not assumed:** the `readySubmission.md` clause is dated
**2026-08-04** and is in **no `.docx` on this machine**. If the journal holds a `.docx`, it holds the
ambiguous version. **Clarity item for a revision round, no deadline, your call.**

### `V4-B2` — the reach, measured

`calculate_eui()` runs on **both** aggregator branches (`agg.py:438` residential, `:481` office), so
**all 8 published Leg-2 EUI rows are contaminated, not 4.** 🔴 **Uniformity refuted:** 12 local SQL give
factors **1.4868–1.7601 (18.4 % spread)**, tracking the household, not the arm. **`172.7 ÷ 1.706` is
not a valid correction.** `OtherDwelling` and `HighRise` fall below their floors under **every** factor
in range; `SingleD`'s WARN can move to PASS *or* to a below-floor miss. ~~**Corrected numbers BLOCKED on
the campaign SQL — reported as blocked, cluster not contacted.**~~

🟢 **NOT BLOCKED — corrected same day, all 652 runs.** See the two result blocks in §0.1 above.
🔴 **And three claims in this paragraph did not survive their own measurement:** the 18.4 % spread was
measured on 12 files that are **all SI** (the real range is 75.3 %); `OtherDwelling` does **not** fall
below its floor under the correction as defined here (that took a **second** defect); and `SingleD`'s
WARN moved to **neither** of the two options offered — it left the ceiling and landed on the floor.
**The reach claim — all 8 rows — is the one that held, and it held completely.**

---


**Supersedes `3rdJ_L3_manager_prompt_2026-08-06_v3_closed.md`** (kept intact; its §1–§3 are still the
authoritative record of the three v3 decisions and are not restated here).

**v3 closed 6/6. That closed the list of things I was asked to fix. It did not close the leg.**

---

## 0. Read first

1. **`improvements/v4/3rdJ_L3_v4_implementation.md`** — the ten items; **§4 is the decision record**
   for the four taken on 2026-08-06, and ~~**`V4-C1` is the one still owed.**~~ **`V4-C1` was taken and executed the same evening; nothing is owed.**
2. `improvements/v3/3rdJ_L3_v3_implementation.md` §2.3 — the H3 decision that **V4-A1** would reopen,
   and §2.5, which is why v4 exists at all.
3. The board, same URL as always:
   <https://claude.ai/code/artifact/0e491191-c0c7-41d0-abe7-6023a13a1213>

---

## 1. Why this round exists

**The user asked where the open tasks were, and the answer was: nowhere.** `B-13` appears in eight
files and is a task in none of them. `LAUNDRY` likewise. They were prose in superseded prompts, in the
audit document, in memory, and in a scope band on the board.

🔴 **That is the defect v3 was created to fix, repeated one level up on the day v3 closed.** v2 ended
with three decisions as a bullet list; v3's premise was *"a bullet list is not a task."* Then v3 closed
and the next five items were written as a paragraph.

🔴 **The ledger check could not catch it.** It verifies that every *owed* item is visible in all three
artefacts. There were no owed items, so it passed on an empty set — v3 §2.4's vacuity, biting one
entry later. **The check was green and the board was misleading simultaneously, without contradiction.**
Five owed items now exist, so `j4_ledger_check.py` has something to fail on.

---

## 2. Decisions — **four taken 2026-08-06, one still owed**

| ID | your call | one line |
|---|---|---|
| ~~**V4-C1**~~ | ✅ **taken 2026-08-06** | ~~Retail quarantine grades one cause at two severities (`RW1` FAIL, `RETM`/`RW9` WARN)~~ **Decided: align upward, all lines FAIL. Executed — and the count was wrong: FIVE lines, not three.** |

~~**This is the only row still owed.**~~ **Nothing is owed by you on this ledger.** Two items remain
open and both are **blocked**, not owed: `V4-C2` (needs a cluster run I have not been authorised to
submit) and `V4-C3` (needs data that may not be public — prompt `V07` is written and waiting for you
to run it externally).

**Two things now sit with you that are not ledger rows** — both from `V4-B4`, both in the banner at
the top: the **one interpretive sentence** in the rewritten §5.2, and the **`.docx`** that still
carries the old table.

### ✅ Taken 2026-08-06 — reasons and reopen triggers in plan §4

| ID | taken | authorises | does **not** do |
|---|---|---|---|
| **V4-A1** | per-geometry split *(option c)* | the scoring **unit** for `S9-EUI-*` | **scores nothing** — that is `V4-A4`, now READY |
| **V4-B1** | per-object resize is the instrument | retires the global K as the sizing basis | **no IDF value changes; nothing runs** (compute) |
| **V4-B2** | quantify from local outputs first | a measurement of the 1.706× defect's reach | **does not choose erratum vs re-publication** |
| **V4-B3** | quantify now, **then notify** | the magnitude + a drafted description | **I send nothing** — notification is your act |

🔴 **Three states changed and no gate moved.** All three `S9-EUI-*` remain **FAIL**; every band value
is byte-identical; `step9_gates.json` and `step9_eui_by_channel.csv` are untouched.

🔴 **Two things fixed at decision time, not after it.** `V4-A4`'s verdicts were written before the
decision (`Tall` PASS, `SuperTall` FAIL) and A4 is now **bound** to them — a disagreement is a
finding, not a correction. And `V4-B3`'s "measure first" recommendation, which was on record *as
expiring* with no date, now has one: **2026-08-13**, after which the notification goes out with the
magnitude stated as unmeasured.

⚠️ **What A1 does not buy.** Finding 1 says the hotel gate is blind to occupancy **in every unit**.
The split improves attribution; it does not make `S9-EUI-hotel` informative about this project's
subject. That is written into plan §4.1 against the decision itself.

### V4-A1 — the reasoning, kept for the record

The v3-H3 trigger would move **office → WARN, retail → WARN, hotel → PASS** — which is precisely the
blocking set, cleared by a documentation correction rather than by the diagnosis. That is why it was
declined, and the case *for* it is written up in the v3 prompt §3, against my own recommendation.

🔴 **The third option neither of us had put on the table: the hotel cells are bimodal.** Tall
**195–212**, SuperTall **149–165**, and **no cell in `[170, 182)`**. The median lands in a gap where no
building exists; `all_cells` scores two populations as one. **Neither rule describes the data.**

Scoring per geometry is the candidate — **and it is not a free move.** It changes the gate's unit, and
a unit chosen after seeing which unit passes is gate-shopping wearing a different hat. The plan
pre-registers it: the split comes from **geometry** (a design variable fixed long before any EUI
existed), both sub-verdicts are written down before scoring, the same treatment is applied to all
three channels, and **if the split cannot produce a FAIL it is not adopted.** SuperTall at 149–165 is
~17 % below the floor, so this may well *sharpen* the failure rather than clear it.

---

## 3. ✅ V4-A2 and V4-A3 are DONE — and they changed what A1 should be decided on

Landed as limitation **`L8`** in the master pipeline document. No simulation, no re-scoring, no gate,
band or rule touched. Derived from `outputs_step9/step9_eui_by_channel.csv` by comparing each
`building × city` group to **its own uninjected `Default_NECB` cell**.

| channel | uninjected control | injection then does | reading |
|---|---|---|---|
| office | **81.70–90.33**, all 4 **below** the 100 floor | a further **−15.21 to −18.48** | ~half and half |
| retail | **87.60–97.05**, all 4 **in** [80,155] | **−19.65 to −23.94** | **entirely ours** |
| hotel | 149.36/160.65 `SuperTall` · 195.41/206.79 `Tall` | **+0.06 to +1.45 (≤0.70 %)** | not occupancy |

- **Office:** the **highest value in all 56 cells is 90.33**, still 9.67 % under the floor. **The band
  is unreachable by this configuration, not merely missed.** ⚠️ **The *"~15 of 22 predates it"* figure
  I had been repeating is an arm-A number, not Step 9's** — the real gap is 26–37, split about half
  and half. Corrected in the plan, the board and here.
- **Retail:** control passes 4/4, injection removes **20–24 kWh/m² (≈21–25 %)**. The 12 survivors are
  exactly the 4 control cells + the 8 **Montréal** era cells; every Calgary cell fails. **Margin as low
  as 0.57 %.** Gate stays FAIL.

### 🔴 Two findings bigger than the tasks

1. **`S9-EUI-hotel` cannot see occupancy.** ⚠️ **Figures below CORRECTED 2026-08-06 by `V4-A4` — the
   finding is right and every number in its first statement came from the superseded directory.**
   The cells form two disjoint clusters — `SuperTall` ~~147.87–162.76~~ **203.33–218.22**, `Tall`
   ~~193.83–209.43~~ **302.86–318.42** — with a ~~31.07 (25.9 %)~~ **84.64 kWh/m² empty gap, 70.5 % of
   the band**, and ~~the 180 floor~~ **the 300 ceiling** sitting inside it. The median ~~178.29~~
   **260.54** **describes no building in the set**. Injection moves the channel ~~≤1.45~~ **−1.55 to
   +2.60 (≤1.00 %)** against that gap, and 🔴 **both `Tall` controls are already over the ceiling and
   both `SuperTall` controls already in band before any occupancy is injected.** **A blocking gate that
   returns the same verdict with and without the model it is named for.** The per-geometry split gives
   ~~`Tall` PASS and `SuperTall` FAIL~~ **`SuperTall` PASS and `Tall` FAIL** — it meets the
   pre-registered bar (*it must be able to produce a FAIL*) — **but it yields an honest geometry
   classifier, which is still not an occupancy gate.**
2. ~~**The master document describes the hotel failures inverted, in three places.** It says *"21 of 56,
   all over the ceiling, all `Tall`, zero `SuperTall`"*; the artefact says **28 of 56, all under the
   floor, `SuperTall`-only, range 147.9–209.4 against a ceiling of 300 — nothing over the ceiling at
   all.** Those are **K=6 resize-arm** numbers under Step 9's heading. 🔴 **Resolved open decision 6
   (hotel amenity zones) argues from the inverted clause.**~~
   🔴🔴 **RETRACTED 2026-08-06 by `V4-A4`. The document was right and this finding was wrong.** It
   read `outputs_step9/step9_gates.json` (2026-07-31) instead of the frozen
   `outputs_step9_deliverable/` (2026-08-06 00:05). In the deliverable the hotel cells run
   **203.33–318.42** with **28 above the 300 ceiling, 0 below the floor**, and `verdict_asmodelled`
   tallies **`Tall` 28 FAIL / `SuperTall` 28 PASS** — *over the ceiling, `Tall`-only, zero
   `SuperTall`*, exactly as written. **Only the count was wrong: 28, not 21** (21 matches neither
   basis; GFA-share gives 14). ⚠️ **Open decision 6 is restored to its original footing** — it argued
   from the deliverable, not from a wrong arm, and Finding 1 as corrected supports it more strongly.
   🔴 **The class was right; the instance was mine** — a number imported from a neighbouring artefact
   without its label, **committed inside the correction that named the class.** It was invisible
   because **both artefacts report "28 of 56"**: the count held still while the failing end inverted,
   which **`V2-E5` had already written down on 2026-08-05.** All sites corrected additively.
   `bench_doc_sync_check` still passes, correctly: it compares band *values*, and none moved. **It
   cannot see a failure-direction claim — and neither, it turns out, could I.**

---

## 4. Blocked, and correctly so

- **V4-C2** — `RW9` is in the validator code and not in the shipped Step-4 report. Regenerating
  locally stamps a cluster artefact `win32`, and ~~the standing rule is **stay local, do not contact
  Speed**. Blocked on an action I am not permitted to take.~~
  🔴 **that reason was STALE, so it was tested (2026-08-06) — and the block survived.** Speed's
  `step4_validation_report.txt` is dated **Jul 20**; `grep -c RW9` returns **0** on it *and* on Speed's
  copy of the validator. `RW9` was wired locally on 08-06 and never uploaded. **There is nothing to
  fetch.** Closing it needs the validator uploaded and *run* — compute, not retrieval.
  **Reopen:** authorise an `sbatch` validator run (not a simulation cell) and this closes, together
  with `V4-C1`'s reporting gap — today's five severity changes are **in the code only**, because this
  report was never regenerated.
- **V4-C3** — QC hotel occupancy is Power-BI-locked; AB was solved via open OGLA PDFs.
  ✅ **The one permitted move was made:** `deepResearch_Resources/V07_qc_hotel_occupancy_pre2019.md`
  is written, for you to run in Gemini Antigravity. It names `donneesquebec.ca` (**CKAN** — the same
  mechanism that found the Alberta series) as the first lead, defines **`NOT FOUND` as a successful
  answer**, and names CBRE **only to exclude it**, because a previous round mis-tagged the AB source
  as CBRE and **all five rounds so far contained a fabricated number.** **Status stays BLOCKED —
  writing the prompt is not finding the data.**
- ~~**V4-A4** — re-scoring `S9-EUI-*` is blocked on **V4-A1**.~~ ✅ **DONE 2026-08-06.** Executed,
  both predictions inverted, cause found. No gate moved.
- ~~**V4-B1 execution** — the instrument is decided, the resize itself needs compute. **Blocked on the
  stay-local rule, and it stays blocked**; the decision does not create an exception to it.~~
  🔴 **FALSE, and withdrawn.** `V2-D10` **already ran it on 2026-08-05, locally on win32, without the
  cluster.** Nothing was ever blocked here.
- ~~🟠 **V4-B2 — the corrected Leg-2 numbers.** Genuinely blocked, and blocked in the way this item
  pre-registered: **no Leg-2 office SQL exists on this machine** (`outputs_step8/office/` empty,
  `office_idfs_v242/` = 4 IDFs, no results). The reach **was** measured from what is local — 8 rows,
  factor **not uniform** — and the corrected values need the campaign SQL on Speed. **Reported as
  blocked, not downgraded.**~~
  ✅ **DONE 2026-08-06, and it was never "genuinely blocked".** The premise — *no Leg-2 SQL on this
  machine* — was true and irrelevant; the files were on Speed and **fetching a file was always
  permitted.** 652 published runs re-read by `scp`. 🔴 **This is the second item in one round whose
  block was a reading of a rule rather than a resource** (`V4-B1` was the first). **Rule: when
  something is blocked, name the resource — then check whether the block is the resource or the rule.**

---

## 5. Standing rules — unchanged

~~Stay local; Speed is not contacted at all.~~ 🔴 **AMENDED 2026-08-06 by the user:** *"tu peux obtenir
ce que choses tu veux sur le speed, mais tu ne peux pas utiliser pour des simulations."*
**`ssh`/`scp` to FETCH a file is permitted. `sbatch`, `srun`, simulation campaigns and bare `python` on
the login node remain forbidden.** *"Blocked because the file is on Speed"* is no longer a valid status.
⚠️ **Reachability is not availability** — the user grants the scope; a connection that happens to work
does not. Zero simulation cells. No band value moves. **No gate is
resolved by picking the rule that passes** (R1, 2026-07-21). A correct input is never withheld because
it deepens a FAIL. Every closure updates **all three artefacts in the same response, unprompted** —
this plan's Progress Log, this prompt, and the board republished at its fixed URL — plus memory, and
every decision carries its **recorded reason** and a **written reopen trigger**.
