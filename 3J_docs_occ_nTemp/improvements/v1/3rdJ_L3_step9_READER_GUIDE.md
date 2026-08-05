# 3J Leg-3 Step 9 — READER'S GUIDE

**Read this before `3rdJ_L3_improvements_step9.md` (7,646 lines).**
Written 2026-08-04 for reviewers — human or LLM — with no prior exposure to this project.

The Progress Log is **append-only and chronological**. It is a lab notebook, not a report. It records
what was believed at each moment, including beliefs that were later shown wrong and struck **in
place**. That is deliberate — provenance is the point — but it means **a cold reader who quotes a
mid-document paragraph will very likely quote something that was subsequently reversed.**

§1 of this guide is the current state. §2 is the register of everything that was reversed. **Check §2
before quoting anything from the log.**

---

## 0. Orientation — the project in 10 lines

| | |
|---|---|
| **Building** | one mixed-use high-rise, EnergyPlus 24.2.0. Two geometries: `Tall`, `SuperTall` |
| **Channels** | 4 tenant channels — `office`, `retail`, `hotel`, `residential` — plus `residential_common` and `service_MEP` (non-tenant) |
| **Scientific claim** | Canadian **GSS time-use diaries** → per-channel occupancy schedules → injected into the model, replacing NECB 2020 code schedules. Behaviour-derived occupancy changes energy in ways a rescaled code schedule cannot reproduce |
| **Campaign** | **56 cells** = 14 scenarios × 2 geometries × 2 cities (`CLG` Calgary, `MTL` Montréal) |
| **Scenarios** | 3 bundles (`B_cons`/`B_central`/`B_opt`), 4 eras (`Y2005`/`Y2010`/`Y2015`/`Y2022`), 6 one-at-a-time sensitivities (`sens_<channel>_<cons\|opt>`), and **`Default_NECB` — the control with NO injection at all** |
| **Step 9** | the validation layer: **30 gates** scored on aggregated output |
| **Current score** | **17 PASS / 0 WARN / 3 FAIL / 10 INFO**, unchanged across the last several arms |
| **The 3 FAILs** | `S9-EUI-office`, `S9-EUI-retail`, `S9-EUI-hotel` — all three are *absolute EUI level vs an external band* |
| **Status** | pipeline sound; **blocked on whether those three bands apply to this building** |
| **Language** | log lines 1–772 are **French**; everything after is **English** (rule adopted 2026-07-31) |

### Vocabulary you need

- **arm** — one complete 56-cell EnergyPlus campaign under one code configuration. Named `A`…`E`, `H`, `R`.
- **cell** — one simulated building-year. `cell_tag` = `<scenario>__<geometry>__<city>`, e.g. `B_central__SuperTall__CLG`.
- **`T9-n`** — a planned *task* (a code change). **`S9D-n`** — a *decision*. **`FINDING n`** — a defect discovered, numbered in order of discovery. **`P1…P7`, `H1…H11`, `R1…R4`, `C1…C4`, `G1…G7`, `D0…D7`** — pre-registered predictions/gates for one specific experiment; the letters are per-experiment and **do not form one global series**.
- **EUI** — energy use intensity, kWh/m²·yr. Here always **per channel, CFA basis** unless it says `tower`.
- **band** — an external `[lo, hi]` EUI interval a channel is expected to fall inside. The three FAILs are band comparisons.
- **injection** — writing GSS-derived schedules into the IDF. The `Default_NECB` scenario is **uninjected** and is the control.
- **`K`** — the multiplier applied to DHW `Heater Maximum Capacity` in the resize work. Arm R uses **K = 10**.
- **`r`** — T9-13's per-day DHW volume scaling ratio, `mean(occ_day) / mean(occ_reference_day)`.
- **"vacuous gate"** — a project-specific term of art: a check that *cannot fail*, or that fails/passes for a reason unrelated to what it claims to test. **12 classes catalogued.** Finding them is treated as a first-class result; several sections are devoted to gates that turned out vacuous. See §4.
- **"seen failing"** — a standing methodological requirement: a gate is not trusted until it has been *observed* to fail on a deliberately broken input.
- **"pre-registered"** — predictions written into the log with numeric thresholds **before** the run that tests them. Anything not pre-registered is weaker evidence and the log usually says so.

---

## 1. CURRENT STATE — the one page to read

### 1.1 The eight simulated arms

Per-channel EUI, kWh/m²·yr, CFA basis, median of 56 cells.

| arm | what changed | office | retail | hotel | outcome |
|---|---|---|---|---|---|
| `cf69d508` | pre-fix baseline | 71.08 | 75.43 | 178.29 | 3 FAIL |
| **A** | T9-9: restore the plug/light standby floor the injector destroyed | 80.03 | 84.05 | 180.94 | 3 FAIL |
| **B** | T9-10: lighting zone-coincidence, office `n = 3` | 82.69 | *frozen — rejected on mechanism* | 179.72 | 3 FAIL |
| **C** | T9-12: retail lighting re-spec, `k = 0.60` | — | 90.05 | — | 3 FAIL |
| **D** | T9-11: DHW per-capita | — | — | — | **arm REFUTED, withdrawn** |
| **E** | T9-13: DHW volume scaling | — | — | — | 4 PASS / 2 FAIL vs H |
| **H** | FINDINGS 7/8/9 fixed | 81.63 | 89.91 | 182.39 | 3 FAIL |
| **R** | DHW burner capacity × 10 | 81.52 | 89.87 | 271.40 | 3 FAIL |

Net over eight arms: office **71.08 → 81.52**, retail **75.43 → 89.87**, hotel **178.29 → 271.40**.
**The same three gates have been FAIL throughout. The other 27 have been stable and passing.**

### 1.2 🔴 The central problem — none of the three FAILs is an occupancy problem

The decisive evidence is the **`Default_NECB` control**: same geometry, envelope, climate and plant,
**no GSS injection at all**, pure NECB code schedules.

| channel | `Default_NECB` (uninjected) | injected `B_central` | band | verdict |
|---|---|---|---|---|
| **office** | **85.45** | 81.27 | floor **100** | **the code's own reference implementation fails the band by 15 %**, and injection moves office *down*. Median needs **+22.7 %**; eight arms delivered **+14.7 %** total |
| **retail** | 92.13, **4/4 in band** | 86.57 | `[80,155]` | arm R is **54/56**; the two misses are **79.82** and **79.96** against an 80.00 floor — short by **0.23 %** and **0.06 %**. FAILs only because the rule demands 56/56 |
| **hotel** | 178.03 → **260.87** after the resize | — | `[180,300]` | the resize moved the **uninjected** control by the same mechanism ⇒ a pure plant effect, **zero occupancy content** |

**So: office = band applicability. retail = gate threshold. hotel = plant + band. None is an
occupancy-modelling problem — and occupancy is what the paper is about.**

Arms C, E, H and R were attempts to fix, through the occupancy channel, three failures the controls
locate outside it. The unblocking action was **decided on 2026-08-02 (user decision #2: re-derive a
band valid for a *stacked* channel, sourced independently, before looking at our number) and never
executed.** Four more arms were run instead. Same for decision #3 (the CanmetENERGY hotel study).

### 1.3 What is NOT in doubt

Calibrate on this before reading 7,646 lines of problems:

- Attribution closes to **≤ 1e-6** on every cell of every arm. 56/56 cells complete.
- Arm R was verified a strict one-variable contrast: every **non-DHW** end use moved **< 0.005 %**.
- **27 of 30 gates pass consistently — including all four that test the actual scientific claim:**
  - `S9-INJECTION` — injection flips residential occupancy from midday-dominant (NECB, evening/midday ratio 0.22) to **evening-dominant** (GSS, **2.41**). A change of **shape**, unreachable by rescaling.
  - `G8o` / `G8r` / `G8h` — the three occupancy levers are non-degenerate and monotonic on 4/4 geometry×city pairs.
  - `S9-COINC` — **0.937–0.967**: the four channels do not peak together. Mixed-use diversity measured, not asserted.
  - `S9-D20` — energy-vs-occupancy lag: office **0.26 h**, residential **10.56 h**.

**The pipeline is sound. The dispute is three absolute-level EUI bands.**

### 1.4 The eight open questions

Full form with *what is known / what is missing / what would settle it* in log **§0.21.4**.

| Q | question | needs simulation? |
|---|---|---|
| **Q1** | Does a **standalone-prototype** EUI band apply to a channel **stacked** in a mixed-use tower? | no — literature |
| ~~**Q2**~~ | ~~Is the office deficit real, or is the office channel **mis-specified**?~~ **ANSWERED 2026-08-04 — NO.** The IDF audit is done: lighting **is** per-space-type, but occupant density (`0.040015`) and plug density (`7.5028 W/m²`) are **one blanket value each on all 17 space types in both towers — and both are *office* values.** So office is the channel they are plausibly right for; retail / hotel / residential wear office's clothes. **Correcting them moves those three, and cannot move office.** `§0.21.3`'s band-applicability conclusion is *strengthened*. Remainder: whether the office values themselves are right (audit item 5e, opens the NECB tables) | **done — no simulation** |
| **Q3** | Is **"all 56 cells in band"** the right gate rule? (retail misses by 0.06 % / 0.23 %) | no |
| **Q4** | Which arm is the deliverable? H under-serves hotel DHW, R over-serves it | no — the K-sweep data exists |
| **Q5** | Is the hotel DHW **draw** right, independent of plant capacity? | no — one literature figure |
| **Q6** | §0.17 says the undersizing hit all 4 channels; §0.20.3 measures it as **hotel-only** (+124 % hotel vs +5.94 % residential, office **−1.42 %**). Which is right? | no — same tables |
| **Q7** | The scorer's `BENCH["hotel"]` is `[180,300]`; decision #3 put the gate on `[240,300]`. **Stale.** | no — but re-run after fixing |
| **Q8a** | Backward-audit **B-1** *(corrected 2026-08-04 — this row previously carried B-3's number)*: residential occupancy uses `HHSIZE × any-present` with **zero intra-household diversity**, and this reaches the **already-submitted 2J paper**. Fix = falsifier step 1 (one script, minutes) + a limitations paragraph on *perfectly synchronised household presence* | **no** |
| **Q8b** | Backward-audit **B-3**: `RW1`/`RW2` — the gates built to catch a dead retail head — read **teacher-forced numbers from `step4_training_log.csv`**, not the shipped pool. **Leg-3 Step 4 only; does not reach 2J** | **yes — the only one** (one 04E re-run, ~40 min GPU) |

**Eight of nine need no simulation** — Q2 is now answered outright, and the one item that does need
compute is Q8b, which does **not** touch the submitted paper.

---

## 2. 🔴 REGISTER OF REVERSALS — check this before quoting the log

Each row is a claim that appears in the log **as written and believed at the time**, and was later
struck or corrected. The log keeps both, by design. **A search that lands on the original will find a
confident, well-argued, wrong paragraph.**

| # | claim as originally written | status | where corrected |
|---|---|---|---|
| 1 | `T9-1` — demote `S9-EUI-{c}` to INFO | **CANCELLED** — running it before the mechanism test would have been "erasing the FAILs then shopping for a justification" | `### T9-1 … ANNULÉE` |
| 2 | `T9-2` — add an `S9-EUI-TOWER` PASS/FAIL gate | **CANCELLED** — you cannot gate against a reference later shown corrupted | `### T9-2 … ANNULÉE` |
| 3 | "Leg-2's office EUI is **electricity-only**" | **STRUCK** — it is all-fuel **and whole-tower**, so it never validated an office *channel* | `T9-4`, 2026-07-31 |
| 4 | Leg-2's office EUI 172.7 is a building property | **CORRUPTED BY A CODE DEFECT** — `calculate_eui()` filters `TableName` but never `ReportName`, summing **watts as kWh**; factor **1.706×** | `T9-4` |
| 5 | The 3 FAILs are explained by the **"stacked tower / buried channel"** effect | **REFUTED BY MEASUREMENT** — exposure rank came out the *wrong way round* in 56/56 cells; hotel is the *most* buried and the *closest* to its band | `T9-3` |
| 6 | `T9-10`'s retail rule `g = 1 − staff_shoulder_flag` | **WITHDRAWN** — froze retail lighting at 339.0211 GJ across all 13 scenarios. Retail's arm-B PASS was **rejected on mechanism**, not accepted | `T9-12` |
| 7 | `T9-11` DHW per-capita; "DHW falls in every channel" | **REFUTED BY ITS OWN SIMULATION** — residential **+40.8 %**. Draw ∝ instantaneous presence is wrong: being home asleep at 04:00 is presence with no draw. **Arm D is not a product** | 2026-08-01 |
| 8 | `prototype_people` as the T9-13 reference | **NOT VIABLE** — one PEOPLE schedule for all channels, `mean_we = 0.0000` ⇒ division by zero. Replaced by `baseline_series` | 2026-08-01 |
| 9 | `Default_NECB` as the T9-13 baseline | **STRUCK** — it has no injection at all, so the argument for it was true of *every* candidate (a vacuous *specification* argument). Baseline = `Y2022` | 2026-08-02 |
| 10 | **FINDING 6** — "pool vs stock = +58…+102 %, the era jump is largely a frame effect" | **HEADLINE WRONG — my control was invalid.** `assemble_2030()` destroys the office signal (no occupational matching). Real frame effect **≈ ±8 %**, and the ×2 weekend rise is **real 2030 behaviour**. Three statements struck | 2026-08-02, same day |
| 11 | **FINDING 8** — "T9-13 *replaces* specialised DHW schedules" | **MECHANISM WRONG** — it is a **cache-key collision** at `commercial_integration.py:2080-2094`. Consequence: **the original D-A fix was a no-op** | 2026-08-02 evening |
| 12 | The `R > 1.5` premise | **FALSE ON THIS STOCK, struck** — the heaters are hard-sized, and `flow = (P·R)·(s·r/R)` ⇒ **`R` cancels** | 2026-08-02 |
| 13 | `S9-LONG-hotel` PASSES | **VACUOUS PASS** — hotel is uninjected in Y2005/10/15 and injected in Y2022, so the "era spread" is an injection on/off step. Re-specified | `S9D-6` / `T9-7` |
| 14 | `H2` / `H6` second clause | **MIS-SPECIFIED** — explicitly *not* a licence to widen | 2026-08-04 |
| 15 | `C3` | **must be re-specified** — successor given, argued as not-a-widening | 2026-08-04 |
| 16 | §0.17 — "undersizing was **not hotel-only**; residential DHW +11.3 %; a new arm for all 4 channels" | **CONTRADICTED, UNRESOLVED (Q6)** — the aggregated arm measures hotel **+124.09 %**, residential **+5.94 %**, office **−1.42 %**, retail **−0.75 %** | §0.20.3 |
| 17 | "job 1172151 will backfill the moment a `qc1983nu` task ends" | **WRONG** — 120 higher-priority tasks (9362 vs 9356) with 7-day walltimes. Work moved to local compute | §0.18.1 |
| 18 | §0.19 `P4c` — "`S9-EUI-retail` stays PASS" | **BASELINE MIS-STATED** — retail was **already FAIL** at 55/56 in arm H | §0.20.4 |
| 19 | §0.19 `P5` — verdict correct | **PASSED FOR THE WRONG REASON** — predicted Tall lands in `[240,300]`; Tall actually overshot *past 300* | §0.20.4 |
| 20 | `Q8` — "backward-audit **B-3** … reaches the submitted 2J paper … needs compute" | **TWO FINDINGS FUSED UNDER ONE NUMBER** — the content is **B-1** (no compute, one script + a limitations paragraph, *does* reach 2J); **B-3** is a different finding (one GPU job, Step-4 gates only, does *not* reach 2J). Split into `Q8a`/`Q8b` | §0.21.4, 2026-08-04 |
| 21 | `Q2` — office is "19 % below its floor **even uninjected**" | **INJECTED FIGURE UNDER THE UNINJECTED LABEL** — uninjected `Default_NECB` is **85.45 = 14.55 %** below the floor; 18.73 % is injected `B_central`. §0.21.3 always had it right | §0.21.4, 2026-08-04 |

### 2.1 What is STALE (correct when written, invalidated by a later change)

- **The office channel of all nine 2030-family scenarios = 36 of 56 cells**, after the office-2030
  product was re-issued 2026-08-02. **No 2030 office number may be quoted from arms A–E.** `Y2022`
  and the three historical years are untouched.
- **Every office statement crossing the era boundary** is caveated: T9-13's office `r`, `S9-LONG-*`
  office, "office presence falls under WFH" measured against the observed year.
- **The scorer's hotel band** — `[180,300]` in code vs `[240,300]` by decision (Q7).

---

## 3. NAVIGATION — where to find things

Search the log by these header strings (line numbers shift; headers do not).

### By theme

| topic | go to |
|---|---|
| **Current state, open questions** | `§0.21` — read first |
| **Latest result (arm R re-score)** | `§0.19` predictions → `§0.20` result |
| **Why the aggregation ran locally** | `§0.18` |
| **The original 6 decisions** | `Registre des décisions — 2026-07-31` (`S9D-1`…`S9D-6`) — **French** |
| **The 5 user decisions of 2026-08-02** | `USER DECISIONS — 2026-08-02` |
| **Why the office FAIL is not a category error** | `OFFICE END-USE DECOMPOSITION` |
| **The injector defect (biggest single fix)** | `S9D-8 — Located defect` → `T9-9 EXECUTED` |
| **Lighting diversity model** | `T9-10 EXECUTED` → arm B → `T9-12` (retail withdrawn and re-spec'd) |
| **The DHW saga (longest thread)** | `T9-11` → refuted → `T9-13` → `FINDING 8` → its correction → arm E → arm H → the K sweep → arm R |
| **The hotel plant undersizing** | `The hotel DHW plant is undersized by construction` → `K sweep` → `H9/H10/H11 … plant question is CLOSED` |
| **Leg-2 corrigendum (decision 5)** | `T9-4` → `DECISION 5` |
| **Vacuous-gate catalogue** | see §4 below |

### Chronological spine

```
2026-07-31  S9D-1..6 decisions (FR) · T9-3..T9-8 · post-closure investigation
            S9D-7/S9D-8 -> the injector defect located
            T9-9 (standby floor) -> arm A · T9-10 (lighting) -> arm B · T9-12 (retail)
2026-08-01  arms C/D closed · T9-11 REFUTED · T9-13 written
2026-08-02  reference table · FINDINGS 6,7,8,9 · 5 user decisions · arm E
2026-08-03  arm H campaign · DHW-volume verification · hotel plant undersizing found
            autosize refused · K sweep -> K=10
2026-08-04  plant question CLOSED · all-channel resize -> arm R (56 cells)
            4 user decisions · §8E aggregation (local) · Step-9 re-score · §0.21
```

---

## 4. The vacuous-gate catalogue

A recurring theme, and the project's most transferable methodological output. A "vacuous gate" is a
check that cannot fail, or that passes/fails for a reason unrelated to its claim. **12 classes**,
each found the hard way:

1. the gate written as PASS-or-INFO (no failing branch)
2. the gate declared but never coded
3. the explanation that cannot fail
4. the probe that never asks *which PASS gate nothing makes fall*
5. the guard whose discriminator is constant in the ground truth
6. the *specification* argument true of every candidate
7. **pass by omission** — the broken channel sits outside the audit's own filter
8. the audit that cannot see the defect because it inspects the dict, not the saved file
9. the gate whose reference comes from the same source it audits
10. the harness defect that makes the gate silently a no-op
11. the gate measuring a quantity the deliverable discards
12. **(new, §0.20.1)** **the gate whose count is stable while its membership turns over completely** — `S9-EUI-hotel` read **28/56 in both arms H and R**, a *different* 28: SuperTall came up into the band, Tall went out past the ceiling. Reading "unchanged" as "nothing happened" is exactly backwards; hotel DHW rose **+124 %**

Two related **non**-kinds, also recorded: check which counterfactual a gate discriminates by reading
the **untreated control**; and **silence** — a reader returning 0.0 for what it cannot parse blames
the system for its own gap.

---

## 5. Method rules this project runs under

Stated so a reviewer can judge whether the log lives up to them (mostly yes; §0.21.5 lists where not):

1. **Predictions are pre-registered** with numeric thresholds before the run that tests them.
2. **Never widen a band or relax a gate to erase a FAIL.** The remedy is re-specification or an
   explicit `N/A`. **A miss is recorded, not repaired.**
3. **A gate must be seen failing** on a deliberately broken input before it is trusted.
4. **Struck claims are kept, not deleted** — hence §2 of this guide.
5. **Test the control before trusting it** (added after reversal #10, where an invalid control
   produced a wrong headline that a monotonicity guard caught).
6. **Print/assert which copy of a module a cluster job actually loaded** (added after a stale
   `sys.path` shadow nearly invalidated a 112-cell campaign).

---

## 6. Where the artifacts are

| what | where |
|---|---|
| Progress Log | `improvements/3rdJ_L3_improvements_step9.md` |
| this guide | `improvements/3rdJ_L3_step9_READER_GUIDE.md` |
| Step-9 gate scorer | `Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py` (CLI: `--agg-dir`, `--outdir`) |
| §8E aggregator | `Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py` (`--idf-name`, `--jobs`) |
| injector | `eSim_bem_utils/commercial_integration.py` |
| arm H tables / arm R tables | `_local_armR_cache/agg_H_allfix/`, `_local_armR_cache/agg_R_resize/` |
| scorecards, both arms | `_local_armR_cache/outputs_step9_H/`, `outputs_step9_R/` (`step9_gates.json`, 4 CSVs, 5 figures, HTML) |
| backward audit (Steps 1–4) | `improvements/investigation/` |
| cluster campaigns | `speed:/speed-scratch/o_iseri/step8_4split/campaign/out_{A,B,C,D,E,H}_*`, `out_R_resize` |

---

## 7. If you are an LLM asked to advise on this project

Three requests, in priority order:

1. **Answer Q1 first** (§1.4). Everything else is downstream. If no valid stacked-channel EUI band
   exists in the literature, say so — that is a legitimate and useful answer, and it converts
   `S9-EUI-*` to INFO with a published limitation. It must be reached by showing the band
   **inapplicable**, never by widening it.
2. **Do not propose another simulation arm to move `S9-EUI-*`** without first addressing §1.2. Eight
   arms moved office +14.7 % against a required +22.7 %, and its own uninjected control sits below
   the floor.
3. **Check §2 before quoting the log.** Roughly one claim in twenty was later reversed, and the
   reversals are usually more interesting than the originals.
