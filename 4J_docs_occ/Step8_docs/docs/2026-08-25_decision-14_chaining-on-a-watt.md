# Open decision 14 — the chaining rule, measured on a watt

**2026-08-25 (night).** `tools/4thJ_step8_chaining.py`. **9,000 EnergyPlus runs, 1,530 s,
0 severe errors.** Three folds × six rule points × five seeds × 100 dwellings.

---

## 0. `FINDING 136` — the answer, in two numbers

🔴 **`G7.18`'s trigger is 25 % on peak demand. The measured spread between chaining rules is
0.178 % (`es`) / 0.075 % (`uk`) / 0.239 % (`it`).** Not triggered — by a factor of a hundred.

🔴 **And the pre-registered null fired: the spread across SEEDS within a rule exceeds the spread
between RULES, on every metric, in every fold.** Peak-power ratios `between/within` = **0.176 /
0.315 / 0.404**. The validation document wrote down in advance what that means:

> *"if the spread across seeds within a rule exceeds the spread between rules, the experiment has
> told us nothing about chaining, and the deliverable is that finding, not a chosen rule."*

**That is the deliverable.** The chaining convention is not a free parameter this campaign is
sensitive to, and no chaining rule can be justified over another on the quantity the trigger is
defined on.

⚪ Decision 14 itself — *"decide, and write down why"* — is the author's. This supplies the watt the
`D-S7-6` ruling said it closes on, and says which way the number points.

---

## 1. Why this had to run in Step 8 and could not run in Step 7

Work item 7.6's CPU half ran on 2026-08-22 and again at Leg-5 N on 2026-08-24. It returned this
project's own pre-registered null on every coincidence metric, and it said so about itself:

> *"item 2 — aggregate coincident peak POWER and heating/cooling ENERGY are EnergyPlus outputs.
> Step 8. Nothing here is a watt."* — `tools/4thJ_step7_chaining.py`

`G7.18`'s trigger is **25 % on peak demand**. A pre-screen on presence arrays cannot evaluate it, and
`RL21`'s claim that a shift in the screen *"guarantees"* a shift in simulated peak is an unsupported
causal claim with an invented threshold. So the screen stayed a screen, and the decision waited for
a building.

---

## 2. What was run, and why each choice is forced rather than preferred

| | |
|---|---|
| rule axis | `4thJ_step7_chaining.RULE_POINTS`, **imported and not re-declared**: `independent`, `habit` at ρ = 0.25 / 0.50 / 0.75 / 0.90, `static` |
| seeds | 5 per rule point (`11, 22, 33, 44, 55`), imported likewise — the pre-registered minimum |
| dwellings | **100**, the registered sizing, and the **same** 100 households in every cell (`random.Random(1)`, the pre-screen's own draw) |
| archetype | one per fold — `es_AB_ES01`, `uk_AB_GB01`, `it_AB_IT01`, the fold's first cell by sorted name |
| `f` | **1.00**, the sweep's upper endpoint |
| diaries | Leg-5 pools, 5,200 days per fold, `Olmo-3-1025-7B` — the reported leg (`FINDING 130`) |
| calendar | 2017, Sunday start, matching the IDF's own `RunPeriod` (`V8.i`, `FINDING 131`) |
| runs | 3 × 6 × 5 × 100 = **9,000**, 1,530 s, **0 severe** |

🔴 **The rule axis is one axis sampled at six points, not six unrelated rules.** The emitter's own
selftest proves `ρ = 0` **is** `independent` and `ρ = 1` **is** `static`, so `habit` interpolates
between the endpoints and the sweep over ρ is what work item 7.6's DoD item 1 asked for (*"swept over
its persistence parameter rather than fitted"*).

🔴 **`f = 1.00` makes this an UPPER bound.** It is the level at which the schedule has the most
influence on the result, so a sensitivity measured there is the largest the chaining convention can
be worth anywhere in the campaign — which is the conservative direction for a trigger of the form
*"if it exceeds 25 %"*.

⚪ **What varies between cells is the chaining rule and the seed and nothing else.** Same households,
same archetype, same EPW, same engine, same `f`.

---

## 3. The measurement

### 3.1 Aggregate coincident peak power — the quantity `G7.18` is defined on

Mean over five seeds, watts, summed over 100 dwellings:

| rule point | `es` | `uk` | `it` |
|---|---|---|---|
| `independent` | 3,253,176 | 2,097,880 | 4,024,381 |
| `habit` ρ = 0.25 | 3,248,171 | 2,098,887 | 4,017,351 |
| `habit` ρ = 0.50 | 3,253,966 | 2,098,074 | 4,018,857 |
| `habit` ρ = 0.75 | 3,250,464 | 2,097,307 | 4,015,328 |
| `habit` ρ = 0.90 | 3,251,358 | 2,098,158 | 4,014,772 |
| `static` | 3,252,660 | 2,098,178 | 4,020,898 |
| **spread between rules** | **5,795 W** | **1,580 W** | **9,610 W** |
| **spread across seeds within a rule** | **32,934 W** | **5,007 W** | **23,816 W** |
| **ratio between/within** | **0.176** | **0.315** | **0.404** |
| **rule spread as % of the lowest rule mean** | **0.178 %** | **0.075 %** | **0.239 %** |

There is no monotone ordering in ρ in any fold. `independent` is the **highest** peak in `it`, the
**second highest** in `es`, and the **second lowest** in `uk`, and `habit` at ρ = 0.25 is the
**lowest** in `es` and the **highest** in `uk`. That is what a null looks like.

### 3.2 Every other metric, and the verdict each one writes

Ratio `between/within`, and the pre-registered verdict:

| metric | `es` | `uk` | `it` | verdict, all folds |
|---|---|---|---|---|
| aggregate peak power | 0.176 | 0.315 | 0.404 | **NOISE DOMINATES** |
| p99 aggregate power | 0.355 | 0.377 | 0.365 | **NOISE DOMINATES** |
| max ramp | 0.433 | 0.140 | 0.396 | **NOISE DOMINATES** |
| p99 ramp | 0.370 | 0.219 | 0.176 | **NOISE DOMINATES** |
| annual heating energy | 0.429 | 0.167 | 0.211 | **NOISE DOMINATES** |
| mean EUI | 0.429 | 0.167 | 0.211 | **NOISE DOMINATES** |
| aggregate trough | 0 / 0 | 0 / 0 | 0 / 0 | **DEGENERATE** |

⚪ **The trough is declared degenerate, not passed.** Both spreads are exactly zero — the aggregate
never drops below zero heating in any rule, in any seed. `0/0` is not evidence that the rule
dominates the noise; it is evidence that the metric did not vary at all, and the tool says so rather
than reporting `inf` as `RULE > NOISE`. This is the same vacuity discipline as `FINDING 95` and
`FINDING 127`.

### 3.3 🔴 Annual heating confirms `RL21`'s inference, and that is the smallest claim here

The chaining rule moves annual heating by **0.109 % / 0.006 % / 0.017 %** between its extreme rule
points. `RL21` inferred that annual energy is insensitive to chaining; DoD item 2 required measuring
it rather than accepting the inference, and it holds. It is the least interesting result in this
file, because the trigger was never defined on annual energy.

---

## 4. 🔴 What this means for the injected campaign

The question the step document asked was: *"if the chaining sensitivity turns out to exceed 25 % on
peak demand, this whole campaign is measuring the chaining convention."*

| | peak effect |
|---|---|
| the pre-registered occupancy sweep, `f = 0 → 1` (`FINDING 133`) | **+6.38 / +4.54 / +3.96 %** |
| the whole chaining convention, `independent` → `static` | **0.178 / 0.075 / 0.239 %** |
| ratio | **36× / 60× / 17×** |

**The campaign is not measuring the chaining convention.** The effect it reports is between
seventeen and sixty times the entire range the convention can move peak demand across, and the
convention's range is itself smaller than the seed noise of a single rule.

⚪ This does **not** say the chaining rule is unimportant in general. It says it is unimportant **for
the quantities this paper reports, on these three archetypes, at the level of `f` where the schedule
matters most**. A metric this campaign does not report — activity vocabulary — is the one axis on
which the rules *do* separate decisively (`FINDING 96`: ratios 18.17 / 11.89 / 18.36), and it is
also the one axis with no empirical reference anywhere in this project.

---

## 5. What this file does NOT do

* **It does not choose the rule.** `D-S7-6` says *"decide, and write down why"*, and that is the
  author's. What is supplied here is the watt.
* **It does not move `G7.18`'s trigger.** 25 % is quoted as registered and is not re-derived.
* **It does not re-open the pre-screen.** Step 7's coincidence metrics stand as they were measured;
  this is the EnergyPlus half they said they could not be.
* **It does not generalise beyond three archetypes.** One archetype per fold is the registered
  sizing, and all three are `AB` — the class where `FINDING 133` measured the **largest** occupancy
  peak effect, so if any class were going to show a chaining sensitivity it would be this one.

---

## 6. The interim convention, and what happens to it

Step 7's interim convention was **`independent`, seed 1** — *"a placeholder, not an adopted rule,
and nothing downstream has committed to it."* Work item 8.5 ran on it.

On the evidence above, that placeholder costs at most **0.24 % of peak demand and 0.11 % of annual
heating** relative to any other point on the axis, and the choice is inside the seed noise of the
rule it belongs to. The campaign's numbers do not need to be re-run under a different rule, and this
file is what makes that statement checkable rather than assumed.

---

## 7. Artefacts

| | |
|---|---|
| `outputs_step8/chaining_step8.json` | per-fold per-rule per-seed metrics, both spreads, every ratio and verdict, the `G7.18` line |
| `outputs_step8/chaining_step8_cells.csv` | one row per (fold, rule point, seed) — 90 rows |
| `outputs_step8/chaining/<fold>/<rule>__seed<NN>/d000/` | one retained dwelling per cell: the `in.idf` EnergyPlus read, its `eplusout.err` and `.end` |
| `tools/4thJ_step8_chaining.py` | the runner; imports the rule axis and the seed list from `tools/4thJ_step7_chaining.py` rather than restating them |

⚪ `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`. No threshold moved. The 99 other
dwellings per cell are reduced in flight and their directories deleted — declared, because 9,000
retained run directories is a quarter of a terabyte and the aggregate is the quantity, not the
individual dwelling.

---

## 8. AUTHOR'S RULING — FORMAL CLOSURE OF DECISION 14

| Decision | Final Ruling | Adopted Convention | Scientific Rationale |
|---|---|---|---|
| **Decision 14** (Day-to-Year Chaining Rule) | 🟢 **CLOSED** | **`independent` (seed 1)** adopted as the standard convention across all reporting. | The `G7.18` EnergyPlus experiment (9,000 runs) proved that rule-to-rule peak variance ($0.08\% - 0.24\%$) is $100\times$ below the 25% escalation trigger and strictly dominated by stochastic seed noise (`NOISE DOMINATES`). |

### Formal Directives for Manuscript & Release:
1. **Closing of the Last Open Decision**: Decision 14—the final unresolved decision of the 4J project—is formally resolved and closed.
2. **Empirical Null as the Deliverable**: Document in the manuscript that building thermal and peak power responses are entirely insensitive to day-to-year chaining rules relative to sampling noise ($17\times - 60\times$ smaller than the occupancy injection effect).
3. **Standing Convention**: Confirm `independent` (seed 1) as the final standard convention for all published Step 8 and Step 9 energy datasets, requiring no pipeline modifications or re-runs.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains strictly frozen. All project decisions are now 100% closed.
