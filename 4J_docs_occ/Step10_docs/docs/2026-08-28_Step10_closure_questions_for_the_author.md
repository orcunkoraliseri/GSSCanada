# Step 10 — the four questions that stand between here and closure

**Filed:** 2026-08-28 · **Owner:** 4J side · **Audience:** the author (decision-maker)
**Basis:** measurement only — nothing was simulated, written under `openubem/`, re-scored or published to produce this document.
**Companion records:** `2026-08-28_EU-08_EU-09_EU-10_acceptance-closure.md` · `2026-08-26_10.1_chaining-closure-notice.md`

⚪ **How to use this document.** Sections 1–3 are *findings* — they are measured, not proposed, and they do not need
your agreement to be true. Section 4 is the four **questions**, each with its options and the option the 4J side
recommends. Section 5 states what each answer costs and what it closes. Answer inline, or in one line each
(`Q1 = (a)`, …); the answers are what unblocks Step 10.

---

## 0. Where Step 10 actually stands

```
board (live)         12 steps   128 items   116 done / 2 in progress / 10 not started
open items by step   Step 6 -> 1     Step 10 -> 7     Step 11 -> 4     all other steps -> 0
Steps 0-9            closed
OpenUBEM / EU arc    closed  (EU-08, EU-09, EU-10 accepted under D-EU-31, 2026-08-28)
```

Everything still open is on the 4J side, and **seven of the twelve open items are Step 10's**. Step 10 is the critical
path to project closure, and the questions below are the whole of it.

---

## 1. Finding A — nothing is waiting on you, and my earlier statement to the contrary was wrong

Two decisions were carried on the board and in the step documents as *open, waiting on the author*. Both were
re-measured against the primary records, and **both are already discharged**:

| decision | recorded state | measured state |
|---|---|---|
| `D-S6-16` — *"the ceiling alarmed and may not be a ceiling"* | open, awaiting author | 🟢 **RULED (a′), 2026-08-28.** The author delegated the choice; (c′) declined. Record: `writing/4thJ_writeup_notes.md` §8; ruling detail at `IMP/docs/DONE/2026-08-24_D-S6-16_the-ceiling-alarmed-and-may-not-be-a-ceiling.md` §9. |
| `D-S11-2` — the DHW draw-volume validation | open, awaiting author (Step 11 STATUS still says so) | 🟢 **DISCHARGED 2026-08-27** by gate `G9.15`: stock means **200.79 / 201.01 / 199.47** l/dwelling/day against 200 ± 10 %; medians 174.97 / 175.79 / 195.13 printed; gate **seen failing** at 401.58 / 402.03 / 398.93 on doubled draws; battery re-run **13 HIT / 0 MISS / 2 already-failing**. Record: `Step9_docs/4thJ_09_enduseLoads_val.md`. |

🔴 **Consequence.** No decision is pending on the author's desk today. The remaining Step-10 work is **execution and
scoping**, not adjudication — which is why §4 puts scoping questions to you rather than rulings. ⚪ Two records are
**stale and should be corrected additively** when Step 10 closes: the Step-11 STATUS line that still claims `D-S11-2`
is open, and the board card that carries `D-S6-16` as open.

---

## 2. Finding B — items 10.5 and 10.6 were executed by `EU-08`; the §10 table is stale

The §10 WORK ITEMS table of `4thJ_10_ubemRealStock.md` lists **10.5** (the `f = 0` control campaign) and **10.6** (the
injected campaign, `f ∈ {0.15, 0.30, 0.50, 1.00}`, "408 cells") as not started. They are not:

```
eu_campaign_cell_spec_v1.0.json      spec_status FROZEN_PINNED   commit 4bd4cad
                                     n_cells 510 = 102 archetypes x 5 f-levels x 3 folds (es, it, uk)
10.6's "408 cells"                 = 102 x 4 non-zero f-levels   -> the injected arm of that same spec
10.5's control campaign            = 102 x f=0                   -> the zero arm of that same spec
executed (EU-08)                     395 of 510 cells, 1,185 retained manifests (3 replicates)
certified perimeter                  149 cells, 447 manifests, all present
f > 0 perimeter                      121 cells
```

⚪ **So 10.5 and 10.6 are discharged in substance.** What they are *not* is quotable at cell level: `D-EU-31`
(Option A, ruled 2026-08-28) bars cell-level use of the 149, `G8.1`–`G8.4` are NOT SCOREABLE, and the only surviving
fold-level figure is `it` **108.25 kWh/m² ± 0.16 %** re-run tolerance — the tolerance itself measured on **35 of the
74** cells, the claim *numerically stable, not bitwise reproducible*, and never "re-measured". Closing 10.5 and 10.6
is therefore a **book-keeping act** against the acceptance record, not a compute act.

---

## 3. Finding C — `H10` cannot be tested by anything that has been run, and barely by anything that could be

`H10` (pre-declared, §1.1/§1.1a of the step document) states: *at fixed `f`, the occupancy effect on building peak
demand grows with `N_u`, the number of independently diarised dwellings.* It is tested on the coincidence factor
`CF(N_u) = P_peak,building / Σ_zones P_peak,zone` against the one-parameter form
`CF(N) = g_inf + (1 − g_inf)/√N`, reported with residuals. The annual EUI effect is expected null
(92.4–97.5 % diurnal-attenuation prior, recorded pre-run).

**Two independent walls stand in front of it.**

### 3.1 🔴 The executed campaign has `N_u` = 1 in every cell

Read verbatim from a certified manifest
(`openubem/outputs/eu_certified_rerun_2026-08-28/rep1/manifests/es__ES.ME.AB.01.Gen.ReEx.001.001__f030.json`):

```
presence_hid              00035                      <- ONE household id
presence_column_header    HH_es_00035_Presence       <- ONE diary column
chaining_rule             independent
sensitivity_f             0.3
runtime_s                 3.675
completed                 True     severe_count 0     fatal_count 0
energyplus_version        23.1
```

One diary per cell ⇒ **`N_u` = 1 in all 395 executed cells**. `CF(1)` is 1 by definition, so the campaign has no
variance at all in the independent variable `H10` is about. 🔴 **This holds regardless of `D-EU-31`** — even if
cell-level use were permitted, the campaign still would not test `H10`. It is a design property of an archetype
campaign, not a defect in it, and it is why `FINDING 158`/`159` read `CF_phi = 1` in 1,450 of 1,450 cells and
`q99 = peak` in 2,970 of 2,970.

### 3.2 🔴 The real-stock corpus supplies 18 multi-dwelling buildings, against `G10.19`'s 30 per fold

From `Step10_docs/outputs_step10/building_table_exercise_es_uk_it.csv`
(header `building_id,country,zone_count,zone_source,layout_status,footprint_area_m2`):

```
rows 297   zones 1,576   99 buildings per country

layout_status
  REFUSED_BY_LAYOUT_CONTRACT   256
  FALLBACK_PENDING_LAYOUT       23     ES 10 / IT 8 / GB 5    zone counts 1..8
  DWELLING_LAYOUT_EMITTED       18     ES  9 / GB 5 / IT 4    zone counts 1, 2, 2, 3, 3, 3, 4, 4, 6, 6, 8, 10, 11, 20, 28, 28
```

`G10.19` requires **30 buildings per fold** carrying a dwelling layout for the `H10` test to be scoreable. The corpus
supplies **9 / 5 / 4**. Upstream reason: the layout contract (convex, courtyard-free, ≥ 8 m wide) accepted **204 of
4,186** real footprints, and dwelling partitioning is only attempted on those.

🔴 **`H10` is therefore structurally NOT EVALUABLE at the pre-declared strength on this corpus.** No amount of compute
changes that; only a different corpus or a relaxed layout contract would.

---

## 4. The four questions

### Q1 — Scope: how does Step 10 finish, given §3?

| | option | what it means |
|---|---|---|
| **(a)** | 🟢 **Run the 18, report `H10` as INFO** *(4J recommends)* | Simulate the dwelling-partitioned buildings. Report `CF` and the `√N` fit **with `N` declared per building and residuals shown**, explicitly as an **INFO** result. Record `H10` as **NOT EVALUABLE at the pre-declared strength**, with §3.2's census as the stated reason. Closes 10.7 honestly; `G10.19` is recorded FAIL-by-population and never PASS. |
| **(b)** | Enlarge the corpus first | Ingest more neighbourhoods, or ask OpenUBEM to relax the convex / courtyard-free / ≥ 8 m layout contract. Re-opens `D-EU-23` territory, is open-ended in time, and carries no guarantee of reaching 30 per fold. |
| **(c)** | Close with no new simulation | Build 10.8's gate board, mutation battery and dossier from retained artefacts; record 10.3, 10.7 and 10.10 as NOT EVALUABLE. Cheapest and fully compliant — but Step 10 then ends with **no real-stock simulation at all**, and the `CF` shape question is never even described. |

**Why (a).** It is the only option that produces a real-stock number while stating its own weakness in the same
sentence. (c) is defensible but leaves the step's central hypothesis undescribed; (b) buys an unbounded delay for an
uncertain gain.

---

### Q2 — Population: which buildings enter the run?

| | option | what it means |
|---|---|---|
| **(a)** | 🟢 **18 emitted + 23 fallback = 41** *(4J recommends)* | The 18 dwelling-partitioned buildings are **Arm D**; the 23 `FALLBACK_PENDING_LAYOUT` buildings are **Arm F** (coarse / single-zone fallback). Reported **separately**, as 10.7 requires. The Arm D vs Arm F contrast is precisely what `G10.22` asks for — a lower-bound contrast on what dwelling partitioning actually buys. |
| **(b)** | 18 emitted only | Smaller and simpler, but discards the contrast and leaves `G10.22` with no population. |

**Why (a).** The 23 cost roughly 40 % more runtime and supply the only control the step has.

---

### Q3 — Compute: where does it run?

| | option | what it means |
|---|---|---|
| **(a)** | 🟢 **Local Windows box** *(4J recommends)* | EnergyPlus **23.1.0** is already installed here — the exact engine every certified manifest names. Cost estimated from the measured `runtime_s = 3.675`: 41 buildings × 2 cases × 5 `f` levels ≈ **400 runs ≈ 30 minutes serial**. No queue, no staging, no new platform. |
| **(b)** | Speed cluster via `sbatch` | Requires staging EnergyPlus on Speed and introduces a **second platform** into an arc that has deliberately avoided one — recall `EU-08` gap B: `platform` is absent from all 1,185 manifests, and **no two-host claim is available**. |

**Why (a).** This is a minutes-scale job. Sending it to a cluster costs a platform claim we spent the whole arc being
careful not to make.

---

### Q4 — Does `D-EU-31`'s cell-level bar reach this new real-stock campaign?

| | option | what it means |
|---|---|---|
| **(a)** | 🟢 **No — `D-EU-31` is scoped to the 149 certified EU cells** *(4J recommends)* | The scoping is **recorded explicitly** in the step document and in the closure record, so no reader can mistake a real-stock per-building number for a certified-cell number. `D-EU-31`'s reasoning (`FINDING 188`–`191`: a bitwise reproducibility comparison cannot pass reliably on this engine) still applies as a **caution** — real-stock results are reported as *numerically stable, not bitwise reproducible*, exactly as `108.25` is. |
| **(b)** | Ask OpenUBEM first | Send one letter and hold 10.7 / 10.10 until they answer. Safe — but `D-EU-31` is a **4J-side ruling about a 4J-side reporting perimeter**, so there may be nothing for them to answer. |

🔴 **Whatever Q4's answer, the OpenUBEM peer's binding limit is unchanged and is not at issue here:** *retained
artefacts only — no new simulation, no re-run, no job submission, no network*, and the `D-EU-27` re-run budget stays
**SPENT**. That limit governs **the 149 EU cells**. A real-stock campaign on our own corpus, our own driver and our own
box is a different population; Q4 exists to make that distinction explicit **before** anything runs, not after.
⚪ `FINDING 181` remains the EU arc's only open item, and is **not** a licence to spend the budget.

---

## 5. What each answer buys

| answer set | compute | closes | leaves open |
|---|---|---|---|
| Q1 (a) + Q2 (a) + Q3 (a) + Q4 (a) | ~400 runs, ~30 min local | 10.3 (parity smoke), 10.5 and 10.6 (book-keeping, §2), **10.7** (Arm D vs Arm F, `H10` INFO), **10.8** (board + mutation battery + dossier), **10.10** (`CF` and the `√N` fit on real `N` > 1) | `G10.19` FAIL-by-population, stated permanently; 10.11 (OpenUBEM's rotation-origin fix) |
| Q1 (c) | none | 10.5, 10.6, 10.8 | 10.3, 10.7, 10.10 all NOT EVALUABLE; no real-stock simulation exists |
| Q1 (b) | unbounded | nothing today | everything |

⚪ **Constraints that hold under every answer.** No measured-accuracy claim from Step 10; `G10.7` stays INFO
permanently; no stock-level EUI from Arm D; no per-dwelling prediction; `G8.15` inherited as closed under `D-EU-29`;
`93.768` is a two-end-use model total and never a whole-building EUI; `66.868 kWh/m²` is heating-only; `es` is not
quotable at any level, and `uk` is withheld at fold level.

---

*Filed by the 4J side, 2026-08-28. Read-only on the OpenUBEM tree. Answer Q1–Q4 and Step 10 proceeds without further
questions.*

---

## 6. AUTHOR'S RULINGS & DIRECTIVES — STEP 10 CLOSURE

| # | Question / Item | Ruling | Adopted Decision & Specification | Rationale & Directives |
|---|---|---|---|---|
| **Q1** | Scope of Step 10 & `H10` | 🟢 **Option (a)** | **Run the real-stock buildings; report `H10` as `INFO` with `N` declared and residuals shown.** | Closes 10.7 honestly. `G10.19` is recorded as `FAIL-by-population` (9 / 5 / 4 buildings vs 30/fold bar) due to the strict geometric layout contract ceiling, avoiding artificial contract relaxation or open-ended delays. |
| **Q2** | Population | 🟢 **Option (a)** | **Simulate 41 buildings: 18 dwelling-partitioned (Arm D) + 23 fallback (Arm F).** | Provides the essential lower-bound contrast for `G10.22` and Work Item 10.7 to evaluate what dwelling partitioning buys over single-zone massing. |
| **Q3** | Compute Execution | 🟢 **Option (a)** | **Execute locally on Windows box using EnergyPlus 23.1.0 (~400 runs, ~30 min).** | EnergyPlus 23.1.0 matches the certified manifests. Eliminates cluster queuing delays, staging friction, and two-platform divergence claims. |
| **Q4** | `D-EU-31` Scope | 🟢 **Option (a)** | **`D-EU-31` is strictly scoped to the 149 certified EU archetype cells and does not bar the real-stock campaign.** | Real-stock simulations represent an independent 4J population on local hardware, reported as *numerically stable* with declared boundaries. |

### Formal Directives for Step 10 Execution:
1. **Execute Real-Stock Campaign**: Proceed immediately with the local simulation of the 41 buildings across the 5 $f$-levels in Arm D and Arm F.
2. **Discharge Work Items**:
   - Close **10.3** (parity smoke), **10.5** and **10.6** (reconciled as book-keeping against the executed 510-cell matrix per §2), **10.7** (Arm D vs Arm F contrast with `H10` INFO), **10.8** (gate board, mutation battery, dossier), and **10.10** ($CF(N)$ curve fitting).
3. **Record Invariants**:
   - `G10.19` recorded as `FAIL-by-population` permanently.
   - `prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`) remains strictly frozen.
   - Update stale status lines regarding `D-S6-16` and `D-S11-2` to reflect their discharged status.

⚪ All Step 10 questions are formally resolved. Execution is fully authorized to proceed.

---

## 7. ADDITIVE RECORD — `Q3` WAS REVERSED BY THE AUTHOR THE SAME DAY, AND THE CAMPAIGN RAN ON BOTH HOSTS

🔴 **Section 6 is NOT edited. It stands as ruled.** This section records what happened after it.

⚪ **7.1 What the author said.** With the local campaign already running, the author asked
*"tu peux utiliser des ressources de la speed avec de la simulation parallele plus de 32 different
cpu, pourquoi locale?"*, was told that local-only was `Q3` (a), his own ruling, and answered:
*"utiliser le speed, change le decision … soumettre des runs meme a la speed, vas-y"*.
**`Q3` (a) is therefore SUPERSEDED**, and it must never again be cited as a reason not to use Speed.

⚪ **7.2 Why the reversal costs nothing that `Q3` (a) was protecting.** What (a) guarded against was
two hosts producing two answers with no way to tell which. That risk is removed by construction:
**one** set of IDF bytes is emitted on Windows and shipped, EnergyPlus is pinned to **23.1.0 on both
hosts** (the installed Windows build; `/speed-scratch/o_iseri/energyplus_23.1.0.sif` on Speed), and a
refusal `P1` drops any cell whose `idf_sha256` differs between the two. Speed rebuilds no geometry —
it has no `shapely` and no `geopandas` — so the second host varies the **platform** and nothing else.
Speed's extracted **24.2.0** trees are not used and must never be for this campaign.

🟢 **7.3 What the second host bought.** `FINDING 181`'s platform arm had been carried as "the author's
call" because the **EU campaign's** 1,185 retained manifests hold `platform` in **0 of 1,185** and may
not be retrofitted. This campaign supplies the measurement instead: **410 paired cells, `idf_sha256`
matched 410 of 410, `P1` dropped none**, worst relative difference **8.66e-15** on annual heating,
**5.39e-14** on building peak, **3.45e-14** on `CF`, **6.30e-14** on `q99`, and the **same peak hour
in 410 of 410** cells. 🔴 The one quotable sentence: **numerically stable across the two hosts, NOT
bitwise reproducible, over 410 paired cells** — the same wording `D-EU-31` forces on the `it` figure.
It does **not** move `G8.14`, whose platform arm stays NOT SCOREABLE on the EU campaign's own
manifests.

⚪ **7.4 Both hosts ran the whole campaign.** 410 of 410 cells locally and 410 of 410 on Speed
(`sbatch` array **1287967**, 410 tasks), 0 failed, 0 severe, 0 fatal, 0 unstable-heat-balance markers
on either side. Directives 1–3 of section 6 are discharged; `G10.19` is recorded
`NOT_EVALUABLE_FAIL_BY_POPULATION` permanently and no layout contract was relaxed to reach a
population; `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` was checked by refusal `R1` before
every run and is unchanged.

🔴 **7.5 A defect the first local run exposed, recorded because it would have inflated `H10`.** Ten
Arm F buildings, all `PARTITION_AUDIT_FAILED` in the census, **did** emit a layout when re-probed at
`units_per_floor`. The route had been chosen by that probe, so the cells refused — 100 of 410 failed.
Had the refusal been absent, those buildings would have been **promoted into Arm D**, manufacturing
`N_u > 1` for buildings the census refused to partition, in the only population where `N_u > 1`. The
census now decides the arm; the probe result is recorded (`probe_disagrees_with_census_arm`) and never
acted on. Full record: `Step10_docs/impl/2026-08-28_realstock-campaign-two-platform.md`.


---

## 🔴 CORRECTION, ADDITIVE — `FINDING 193`: THE SENTENCE "0 UNSTABLE-HEAT-BALANCE MARKERS" IS **FALSE**, AND WHAT IS ACTUALLY THERE IS `FINDING 182` REPRODUCED ON AN INDEPENDENT CORPUS

🔴 **The wrong claim is left in place above and corrected here.** §Verified and §7.4 of the
questions doc both say *"0 severe, 0 fatal, 0 unstable-heat-balance markers"*. The first two are true.
**The third is not.** The scored board never said it — `realstock_gate_board.json` records
`G10.15.diverging_heat_balance_markers = 190` — so this is a prose error against our own artefact,
which is the class `V10.h` exists for.

⚪ **What is measured.** **190 of 410** cells carry one marker each, and the distribution is not
random: **190 of 190 `es` cells carry it and 0 of 220 `uk` + `it` cells do.** Identical on **both
hosts** — Speed's `speed_metrics.jsonl` splits 190 / 220 exactly the same way — so it is **not** a
platform artefact and it does not disturb the platform arm.

⚪ **What the marker is, read from the `.err` rather than named from memory.**
`** Warning ** Temperature out of range [-100. to 200.] (PsyPsatFnTemp)`,
`Routine=PsyTwbFnTdbWPb, During Sizing, Environment=ANNUALSIZINGPERIOD`, input temperature
**−126.168377 °C**. The recurring-error summary reports it **1 total time, 0 during Warmup,
0 during the annual run**. 🔴 **It therefore enters no hourly series, no annual total, no peak,
no `CF` and no `q99`** — every number in this document stands. 410 of 410 completed on both hosts,
0 severe, 0 fatal: still true.

⚪ **The `es` weather file is clean, so the −126 °C is generated inside EnergyPlus.**
`es_madrid_2009_2010_y2010.epw`: 8,760 rows, dry-bulb **−5.3 … 37.3 °C**, dew point
**−12.4 … 17.3 °C**, no sentinel values, and 12/26 13:00–16:00 reads 3.2 / 4.2 / 5.0 / 6.8 °C.
The out-of-range temperature is produced by the **sizing period** on that weather, not read from it.

🔴 **Why this is worth a finding rather than a typo fix.** `FINDING 182` recorded `marker_psy`
as **perfectly confounded with the `es` fold** on the EU campaign's certified cells. This campaign
**reproduces that confounding at 190 of 190** while sharing **no cell, no footprint, no archetype and
no injection** with it. The only factor common to both is the **`es` weather basis**, and the file
itself is clean — which points at the sizing-period construction on that weather and away from the
geometry, the campaign and the platform. ⚪ **It is an OpenUBEM-side observation, raised as a
measurement; nothing here diagnoses their sizing objects.**

⚪ **What moves on the board: nothing.** `G10.15` was already `OPEN_INHERITED` and is now open with
a **measured, structured population** instead of a clean count — which is the gate working. No
threshold moved, no verdict changed, `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.
