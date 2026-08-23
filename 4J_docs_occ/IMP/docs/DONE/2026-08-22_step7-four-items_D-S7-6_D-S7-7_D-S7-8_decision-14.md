# Four items for the author — everything Step 7 still waits on a person for

**Date:** 2026-08-22 (night)
**Raised by:** the close of the GPU-free plan `T1`–`T5` (`Step7_docs/4thJ_07_schedules_and_chaining_IMP.md`, 591 lines).
**Status:** all four OPEN. **Nothing in this file changes any artefact.** No gate re-scored, no tool
edited, no schedule re-emitted, `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.

**Why the four are in one document:** they are the complete set of things that need a *person*. Every
other Step 7 item is owed to the GPU queue and needs nothing from anybody — work item 7.2 →
`G7.12` (a 7-minute re-run, staged, waiting only for job `1286209` to release the A100), the Leg-5
campaign → every reportable diary, the untuned-base arm → `G7.7` control 1, the rejection control
→ `G7.9`.

| # | Item | What is actually asked | Weight |
|---|---|---|---|
| **Q1** | `D-S7-6` (`FINDING 93`, and now `FINDING 98`) | how households enter the synthetic population | 🔴 **no household-level result can be claimed until this is ruled** |
| **Q2** | `D-S7-7` (`FINDING 94`) | presence signal, or activity-resolved internal gains | 🟡 one methods sentence either way; the artefacts for both already exist |
| **Q3** | `D-S7-8` | which calendar year a schedule runs on | 🟡 inert today, 🔴 becomes a basis choice the moment Step 8 attaches weather |
| **Q4** | **open decision 14** | what closes it, now that the CPU pre-screen has returned a null | 🔴 the last open decision in the project |

🔴 **One provenance ceiling covers Q1, Q2 and Q4 alike:** every generated diary that exists offline is
the Leg-4 rehearsal on `allenai/OLMo-2-0425-1B`, `N = 600` per fold, stamped
`LEG-4 PILOT -- NOT REPORTABLE`. What the tooling and the gates establish is real; **no diary number
below is a result.**

---

# Q1 — `D-S7-6`: how do households enter the synthetic population?

## 1. The question in one paragraph

Work item 7.6 asks for **100 households**. Step 5 cannot supply one. `population_<c>.csv` is a
**person** table — `country, strat_age_band, strat_sex, strat_hh_type, strat_econ_status,
strat_day_type`, 100,000 rows — with **no household identifier**. `D-S5-9` settled household *type*
on a person basis (`FINDING 60`, convention A) and never needed to assemble a dwelling, so nothing in
Step 5 says which synthetic persons share a roof. The chaining experiment was therefore run on
composition taken from the **real corpus** (`hid` / `pid`): real households wearing generated days.
That is a sample of **surveyed** households, not a sample of the synthetic population, and the two are
not the same object.

## 2. 🔴 `FINDING 98` — and the fallback is weaker than "surveyed households" makes it sound

Measured on `harmonised.parquet` (2,024,068 episodes, 73,254 diaries) by grouping `(country, hid)`.
**A `hid` group is the set of household members who kept a diary, not the household.**

| | `es` | `uk` | `it` |
|---|---|---|---|
| `hid` groups | 9,541 | 4,229 | 18,435 |
| mean diarists per group | 2.006 | 1.876 | 2.075 |
| groups with exactly **one** diarist | 31.46 % | 39.44 % | 35.28 % |
| 🔴 **... of which the members are NOT labelled `one_person`** | **13.50 %** | **12.37 %** | **2.98 %** |
| `couple_with_children` groups | 3,875 | 719 | 6,331 |
| ... represented by a **single** diarist | **10.50 %** | **11.96 %** | **1.58 %** |
| ... mean diarists in them | 2.46 | 2.25 | 3.03 |

🔴 **So between 3 % and 13.5 % of the "households" the experiment runs on are multi-person households
represented by one person**, and the share is **country-correlated with a 4.5× spread** (`es` 13.50 /
`uk` 12.37 vs `it` 2.98). A `couple_with_children` household contains at least three people; on `es`
and `uk` roughly one in nine of them contributes a single diary. **The co-presence half of `G7.4`
therefore sees partners and children who have no day at all** — and it will read that absence as
structure. ⚪ Zero groups mix household types, so the label itself is internally consistent; what is
missing is people, not consistency.

This does not change what was run. It changes what option (a) below is allowed to claim: not
"surveyed households", but **"the diarist members of surveyed households"**.

## 3. The three options

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Leave it. The chaining experiment stays on surveyed composition, and the paper says so — with `FINDING 98`'s per-fold numbers, not a general caveat.** | Costs nothing and re-opens nothing. 🔴 The declaration has to be specific: household-level quantities (`mean_pair_corr`, `trough_aggregate`, co-presence) are measured on partially observed households at a rate that differs 4.5× by country, so they are read **per fold or not at all**. It joins the asymmetry table the paper already owes (`FINDING 53`, `D-S6-2`, `FINDING 51`, `FINDING 60`) |
| **(b)** | Add a household identifier to Step 5 by drawing **households** rather than persons | 🔴 **Step 5 basis change.** Step 5 closed on 2026-08-22 with a 36-gate board and a declared DoD exception; re-opening it invalidates `population_*`, `prefixes_*`, and every `G6.1` null raked onto them. It also needs a household-size-by-type joint the census route never delivered — `D-S5-9` chose convention A precisely because `QS112UK` forced it |
| **(c)** | Assemble households post hoc by grouping synthetic persons of compatible `strat_hh_type` | 🔴 The invention class `FINDING 47` is about. Nothing in Steps 1–5 measured which ages, sexes and economic statuses co-reside; grouping on type alone would manufacture a joint distribution and then read household coincidence off it |

⚪ **What is NOT in question:** the person-level schedules. Presence per person comes from that
person's own stratum and its back-off ladder, and no household assumption enters it. The question
scopes to household-level metrics only.

---

# Q2 — `D-S7-7`: presence signal, or activity-resolved internal gains?

## 1. Two documents, and only one of them can be implemented

| document | what a schedule carries |
|---|---|
| `4thJ_07_constrainedGeneration.md`, DIARIES TO SCHEDULES | *"**Activity-resolved internal gains**, which is the part a presence fraction throws away"* |
| `D-S8-2` item 5, ruled 2026-08-21 and pre-registered | `phi_int(t) = (1-f)*3.0 + f*3.0*g(t)/mean_year(g(t))`, `g(t)` = *"the generated presence signal from `G7.13`"* |

The second is a **fraction**. The first is a **watt**. Turning a 3-digit HETUS activity code into a
power needs a mapping, and **there is no admissible one**: `RL25` was commissioned for exactly that
and its Part C figures were rejected as unsourced — mechanisms real, numbers not. Inventing one here
would place an invented number between our diaries and every load in the paper.

🟢 **The emitter already implements the ruled interface** (presence) **and keeps each pool day's
activity codes beside it**, so reinstating activity-resolved gains later needs no GPU run — only a
mapping.

## 2. The two options

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Presence, as `D-S8-2` item 5 already ruled. The methods say in one sentence that internal gains are occupancy-redistributed and NOT activity-resolved.** | Nothing to build; it is what exists and what is pre-registered. Without that sentence `D-S8-2` item 5's own wording reads as if the gains were activity-resolved, which would be a claim we cannot support. The `f`-sweep is unaffected: it is a sweep of how much of a fixed 3.0 W/m² annual mean follows occupancy |
| **(b)** | Reinstate activity-resolved gains | 🔴 Blocked on a source, not on effort. It needs a published activity→power table admissible under `FINDING 47`'s standard (volume, issue, pages, first author), and `RL25` failed to find one. Until such a source exists this option cannot be executed, only promised |

🔴 **Whichever is ruled, one sentence must move**: today the two documents contradict each other, and
a reader who takes the parent implementation at its word will believe the paper resolves activities
into watts.

---

# Q3 — `D-S7-8`: which calendar year does a schedule run on?

## 1. What was used, and on what basis

`es` **2010**, `uk` **2014**, `it` **2013** — recorded in every `manifest.json` and every `.idf`
header. It is a CLI parameter with **no default**, and leap years are refused outright (366 days =
8,784 h; silently dropping 29 February shifts every weekend after it while still looking plausible).

🔴 **The recorded rationale — "the non-leap year of each survey pair" — selects nothing.** Checked:
ES 2009-2010, UK 2014-2015, IT 2013-2014. **None of those six years is a leap year.** The rule as
written does not discriminate between the two candidates in any fold, so the three years in use were
picked without a criterion.

## 2. 🟢 The choice is inert today — and that is the useful part of the answer

All six candidate years are identical in day-type **composition**:

| year | days | weekdays | Saturdays | Sundays | 1 Jan falls on |
|---|---|---|---|---|---|
| 2009 | 365 | 261 | 52 | 52 | Thu |
| 2010 | 365 | 261 | 52 | 52 | Fri |
| 2013 | 365 | 261 | 52 | 52 | Tue |
| 2014 | 365 | 261 | 52 | 52 | Wed |
| 2015 | 365 | 261 | 52 | 52 | Thu |

So switching years cannot change a mean presence, a day-type share, or any annual aggregate the
emitter produces. What it changes is the **ordering** — which calendar date is a Saturday. That is
irrelevant while the schedules stand alone, and it becomes a basis choice the moment `D-S8-2` item 6's
**actual-meteorological-year** file is attached: the schedule's weekends must land on the weather's
weekends, or the campaign pairs a synthetic Sunday with a real Tuesday for 52 weeks.

⚪ Recorded, not a finding: the emitter's day types are `weekday / saturday / sunday` only. **Public
holidays are simulated as ordinary weekdays** in every country. That is a property of the corpus's own
`strat_day_type` and not a defect introduced here, but the year choice cannot repair it either.

## 3. 🔴 This is the same question as `D-S8-2` item 6, and the corpus cannot answer either

`D-S8-2` item 6 ruled diary-survey-year actual weather and proposed — *to be confirmed against the
published methodology* — that "survey year" means **the twelve consecutive months containing the most
diaries.** Checked against what we hold: **that rule is not computable from our data.**

`harmonised.parquet` carries **no diary date and no diary year**. It carries `wave` (`2009-2010`,
`2014-2015`, `2013-2014`) and `strat_season_raw`, and the season field is not the same object in the
three countries:

| fold | finest date information in the delivery | diary distribution across it |
|---|---|---|
| `es` | `TRIM`, calendar quarters. 🔴 **No month-level field exists anywhere in the Spanish delivery** (`F-ES-9`) | 25.60 / 26.19 / 25.11 / 23.10 % |
| `it` | `meseri`, ISTAT's own protective bands **Nov-Jan / Feb-Apr / May-Jul / Aug-Oct**, not readable finer (`F-IT-2`) | 26.56 / 25.44 / 24.12 / 23.89 % |
| `uk` | `dmonth`, all twelve months | 5.42 % (Dec) to 12.12 % (Oct) |

Two consequences. **(1)** Fieldwork is spread over the whole annual cycle in all three countries — no
quarter is under 23 % — so neither year of a pair is "the" year of the survey; both are partial.
**(2)** One of Italy's four bands (**Nov-Jan**) straddles the calendar-year boundary by construction,
so roughly a quarter of Italian diaries cannot be assigned to a calendar year **even in principle**
from the data we hold. Fixing the twelve-month window is a **documentation** task — the published
fieldwork calendars — not a data task, exactly as `D-S8-2` item 6 already says of items (1)–(3).

## 4. The three options

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Rule the *rule*, not the year: the schedule calendar year is the first calendar year of whatever twelve-month window `D-S8-2` item 6 fixes, and the schedules are re-emitted once that window is known.** | Costs nothing now (re-emission is CPU-seconds and every cell is a pilot cell anyway), and it makes schedule and weather share one calendar by construction instead of by coincidence. It also removes the empty "non-leap" rationale from the record |
| **(b)** | Freeze `es` 2010 / `uk` 2014 / `it` 2013 as they stand and declare the choice arbitrary | Honest and cheap, but it hands Step 8 a schedule calendar chosen before the weather window and guarantees a re-alignment argument later. If the window turns out to start in the *other* year, either the schedules or the weather is off by one weekday for 8,760 hours |
| **(c)** | Run **both** years of each pair as a sensitivity | Doubles a campaign to measure something the table in §2 shows is compositionally identical. Only worth it if the author wants the weather-alignment effect itself quantified, which is a Step 8 question with an EnergyPlus price tag |

---

# Q4 — open decision 14: what closes it?

## 1. Where it now stands

Decision 14 — the day-to-year chaining rule — is **the only decision in the project still open**, and
`RL21` established it cannot be closed by citation: no published study compares chaining rules on the
same building. It closes by our own experiment or not at all. The registered experiment is `G7.18`:
three rules, 100 households, one archetype, **≥ 5 seeds**, scored on annual peak electrical power and
heating/cooling ramp rates, reported not thresholded, with one escalation trigger — *if peak demand
differs by more than 25 % between rules, the chaining method dominates the downstream result.*

The CPU half ran on 2026-08-22: **90 cells** (3 folds × 6 rule points × 5 seeds, 100 households,
8,760 h each), `tools/4thJ_step7_chaining.py`, selftest 40/40. It returned **the pre-registered null**:

| | result |
|---|---|
| coincidence metrics (`annual_mean`, `mean_pair_corr`, `max_ramp`, `trough_aggregate`) | 🔴 **seed noise dominates on at least two folds of three; on `mean_pair_corr` on all three** |
| `peak_aggregate`, `p99_aggregate` | ⚪ **degenerate** on `es` and `it` — pinned at exactly 1.000 in all 30 cells: at 100 households some hour has everyone home |
| `vocab_month_mean` | 🟢 rule effect **18.17 / 11.89 / 18.36 ×** the seed spread |
| `jaccard_adjacent_same_day_type` | 🟢 **71.64 / 64.50 / 63.77 ×** |
| `vocab_day_mean` (negative control) | 🟢 1.02 / 0.30 / 0.44 — the harness manufactures nothing |

So the rule is **invisible in coincident occupancy and decisive in activity vocabulary**, and those
are two different claims about two different quantities. 🔴 And `FINDING 96`: the one criterion
`RL21` offered as empirically anchorable — distinct activity codes per person per **month** — has
**no reference anywhere in this project**. ISTAT and Spain give every respondent exactly one diary
day; only the UK has a second, and in **99.7 %** of those 7,920 cases the two days are a weekday and a
**weekend** day. The habit rule holds the previous day *of the same day type*, so it cannot touch that
step, and the measurement confirms it: cross-day-type Jaccard moves by **0.0030 / 0.0014 / 0.0022**
across all six rule points.

## 2. What the null does and does not license

The step document registered the caution in advance — the pre-screen is *"a **screen, not a
substitute**; `RL21` claims a shift in it 'guarantees' a shift in simulated peak, which is an
unsupported causal claim with an invented threshold."* The run makes that concrete **from the other
side**: the screen does not shift at all, so it cannot guarantee anything either way. 🔴 **Whether
peak demand shifts between rules is still entirely unmeasured**, and nothing in the 90 cells may be
substituted for `G7.18`'s trigger — none of it is a watt.

⚪ The three baseline schedule cells currently on disk use `independent`, seed 1. That is a
**placeholder, not an adopted rule**; nothing downstream has committed.

## 3. The three options

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Keep `G7.18` and scope it to the minimum that satisfies its own registration: one archetype per fold, one `f` level, 3 rules × 5 seeds. Decision 14 closes there, in Step 8, with a written reason.** | It is the only option that produces the watt the trigger is defined on. Sizing, as arithmetic from the registered spec: 3 rules × 5 seeds × 100 dwellings = **1,500 dwelling-years per fold**, 4,500 across three — **independent of** the 510-archetype `f`-sweep, since one archetype and one `f` are held fixed. 🔴 It is blocked behind an IDF that does not exist and five open §6 geometry/zoning decisions, so ruling (a) is a ruling about **order**, not a green light |
| **(b)** | Close decision 14 now on the vocabulary axis: adopt `habit`, `rho` declared as a sensitivity, and report the coincidence null as the deliverable | Cheapest, and defensible on the evidence that exists — the ordering is monotone in `rho` on all three folds and would survive a bigger pool. 🔴 But it closes the decision on the one axis **no survey in this project can anchor** (`FINDING 96`), and it silently drops DoD item 2, which requires *both* metrics. The paper would then choose a chaining rule on a criterion with no reference value |
| **(c)** | Declare decision 14 unresolvable, adopt `independent` as a stated convention, and report both nulls | Maximally honest and the weakest result: the paper would say the schedule-assembly convention was never tested against demand. It also leaves `RL21`'s claim standing unchallenged when we are the only people positioned to test it |

## 4. 🔴 One thing that must happen before any of the three, and it needs no ruling

Every number in §1 comes from **600-diary Leg-4 pools on a 1B backbone**, whose back-off ladder serves
four days in ten from a stratum coarser than the person's own (`es` 57.79 / `uk` 62.33 / `it` 63.52 %
full depth). The **vocabulary ordering** would survive a bigger pool. **The seed-noise verdicts might
not** — a larger pool narrows the within-rule spread and could turn a coincidence metric from "tells
us nothing" into a real effect. 🔴 **The pre-screen must be re-run at Leg-5's `N ≥ 5,200`, and the
back-off ladder re-measured rather than assumed to have improved, before any verdict in §1 is written
into the paper or used to justify option (b) or (c).** That re-run is CPU-only and costs minutes once
Leg-5 lands.

---

# What changes on disk when each item is ruled

| item | ruled | what moves |
|---|---|---|
| `D-S7-6` | (a) | one declaration paragraph in Step 7 + a row in the paper's asymmetry table. No code |
| | (b) | Step 5 re-opens: `population_*`, `prefixes_*`, `G6.1`'s null, the Step 5 board |
| | (c) | a new assembly tool, and a joint distribution nothing measured |
| `D-S7-7` | (a) | one methods sentence; the parent implementation doc's DIARIES TO SCHEDULES line is corrected |
| | (b) | blocked until an admissible activity→power source exists |
| `D-S7-8` | (a) | the three pilot cells are re-emitted when `D-S8-2` item 6 fixes the window (CPU-seconds); the "non-leap" rationale is struck from the record |
| | (b) | one recorded declaration |
| decision 14 | (a) | nothing now — it becomes the first thing Step 8 runs once an IDF exists |
| | (b)/(c) | `outputs_step7/chaining_experiment.md` is written and DoD item 6 closes |

**Nothing is blocked on these four.** Job `1286209` (Leg-5 `es`) is running and owns the only A100
`7g.80gb` slice; `G7.12`'s 7-minute re-run is staged behind it. The four items above can be ruled at
any time, in any order, and none of them stops a job from being submitted.

---

## Answer box

> **Q1 — `D-S7-6` (Household representation):** (a) surveyed composition / (b) re-open Step 5 / (c) synthetic assembly  → **(a) Surveyed composition — declare as "diarist members of surveyed households" with `FINDING 98` per-fold numbers.**
>
> **Q2 — `D-S7-7` (Internal gains interface):** (a) presence signal / (b) activity-resolved  → **(a) Presence signal — follow `D-S8-2` Item 5 (occupancy-redistributed 3.0 W/m² baseline); correct the parent implementation text.**
>
> **Q3 — `D-S7-8` (Schedule calendar year):** (a) rule the rule / (b) freeze arbitrary years / (c) both years  → **(a) Rule the rule — schedule year aligns to the first calendar year of the `D-S8-2` Item 6 weather window; re-emit schedules once fixed.**
>
> **Q4 — Open Decision 14 (Chaining rule closure):** (a) close via `G7.18` in Step 8 / (b) close on vocabulary now / (c) declare unresolvable  → **(a) Close in Step 8 via `G7.18` EnergyPlus peak demand trigger (1 archetype/fold, 1 $f$-level, 3 rules × 5 seeds); re-run CPU pre-screen at Leg-5 ($N \ge 5{,}200$).**

---

## Author's Rulings & Directives (2026-08-22)

| # | Item / Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|---|
| **Q1** | `D-S7-6` (Households / `FINDING 98`) | 🟢 **Option (a)** | **Retain surveyed diarist composition**; state explicitly as *"the diarist members of surveyed households"*; record per-fold participation rates in the paper's asymmetry table. | Add declaration paragraph in Step 7 docs; no re-opening of closed Step 5 basis. |
| **Q2** | `D-S7-7` (Gains / `FINDING 94`) | 🟢 **Option (a)** | **Presence signal (`phi_int(t)`)** as pre-registered in `D-S8-2` Item 5; state clearly in methods that internal gains are **occupancy-redistributed** and not activity-resolved in watts. | Correct parent implementation text in `4thJ_07_constrainedGeneration.md`. |
| **Q3** | `D-S7-8` (Calendar Year) | 🟢 **Option (a)** | **Define schedule calendar year as the first calendar year of the 12-month weather window** established under `D-S8-2` Item 6; strike the "non-leap" rationale. | Re-emit schedules once fieldwork weather window is fixed in Step 8 (CPU-seconds). |
| **Q4** | **Decision 14** (Chaining Closure / `G7.18`) | 🟢 **Option (a)** | **Close Decision 14 in Step 8 on the pre-registered EnergyPlus peak demand trigger (`G7.18`)** across 1 archetype/fold, 1 $f$-level, 3 rules × 5 seeds (1,500 dwelling-years/fold); re-run CPU pre-screen at Leg-5 ($N \ge 5{,}200$). | Maintain `independent` as interim placeholder; execute `G7.18` EnergyPlus battery once Step 8 geometry and IDF generation are operational. |

---

### Detailed Rulings and Directives

#### 1. Q1 (`D-S7-6`): Representation of Synthetic Households
* **Choice**: Option (a) — Maintain surveyed household diarist composition with explicit per-fold accounting.
* **Scientific Rationale**:
  1. Re-opening Step 5 (Option b) to generate household-level synthetic populations would invalidate all raked marginals, prefix tables, and Step 5/6 gates that successfully closed.
  2. Synthesising household joint demographics post-hoc (Option c) would invent an unmeasured joint distribution.
  3. Fully disclose `FINDING 98` in the methodology: household metrics (`mean_pair_corr`, `trough_aggregate`, co-presence) are evaluated over the observed diarist members of surveyed households (with 1-person diarist representation in multi-person households at $13.5\%$ in ES, $12.4\%$ in UK, and $3.0\%$ in IT), reporting household metrics per fold.

#### 2. Q2 (`D-S7-7`): Internal Heat Gains Modeling
* **Choice**: Option (a) — Use the occupancy presence fraction from `G7.13` to modulate the baseline 3.0 W/m² internal heat gains, as registered in `D-S8-2` Item 5.
* **Scientific Rationale**:
  1. No empirically grounded, scientifically rigorous mapping from 158 HETUS activity codes to appliance/metabolic wattage exists in public literature (`RL25`).
  2. Modulating a fixed 3.0 W/m² annual baseline by normalised daily presence ($\phi_{\text{int}}(t) = (1-f)\cdot 3.0 + f\cdot 3.0\cdot g(t)/\bar{g}$) avoids ungrounded parameter invention while capturing diurnal occupancy-driven load variation.
  3. Correct the wording in `4thJ_07_constrainedGeneration.md` to prevent any misleading impression that activity codes are converted directly into watts.

#### 3. Q3 (`D-S7-8`): Alignment of Calendar Schedules and Weather
* **Choice**: Option (a) — Dynamically couple the schedule calendar year to the start of the 12-month actual meteorological year (AMY) selected under `D-S8-2` Item 6.
* **Scientific Rationale**:
  1. Survey fieldwork spans all seasons across two-year survey waves (2009–2010 for ES, 2014–2015 for UK, 2013–2014 for IT).
  2. All candidate non-leap years possess identical day-of-week distributions (261 weekdays, 52 Saturdays, 52 Sundays).
  3. Aligning the schedule calendar year directly to the empirical weather window ensures that weekend occupancy profiles correctly coincide with weekend meteorological conditions for all 8,760 hours of thermal simulation.

#### 4. Q4 (Open Decision 14): Closing the Day-to-Year Chaining Rule
* **Choice**: Option (a) — Resolve Decision 14 in Step 8 using the pre-registered `G7.18` EnergyPlus peak electrical demand and ramp-rate experiment.
* **Scientific Rationale**:
  1. The CPU pre-screen confirmed that day-to-year chaining rules exhibit strong vocabulary differentiation ($11\times - 71\times$ effect) but lack an empirical benchmark in survey microdata (`FINDING 96`).
  2. The decisive engineering question is whether chaining choices alter building peak electrical demand and thermal load ramps by $> 25\%$.
  3. Sizing for Step 8 is fixed at 1 archetype per fold, 1 internal gain level ($f$), 3 rules (independent, Markov, habit) $\times$ 5 seeds = 1,500 dwelling-years per fold.
  4. Prior to Step 8 simulation, re-evaluate the CPU pre-screen on the full Leg-5 dataset ($N \ge 5{,}200$) to confirm whether coincident occupancy variance narrows with scale.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains untouched and verified. Nothing is running on Speed.
