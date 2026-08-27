# Step 10 — Real-stock UBEM simulation with per-dwelling diaries

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 10. Validation: `4thJ_10_ubemRealStock_val.md`
#### Engine: **OpenUBEM** — `C:\Users\o_iseri\Desktop\OpenUBEM\`. Boundary contract: `MVP_european_locations.md` §9.4 and §12.11.
#### Origin of the design: `../Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md` (unified OpenUBEM + GSSCanada architecture).

---

## STATUS

🟡 **PLANNED 2026-08-26. FOUR WORK ITEMS BUILT, 2026-08-26 / 27 — the STATUS line said "nothing built"
until 2026-08-27 and was stale by four items.** Done: **10.1** (chaining closure notice), **10.2**
(`D-S10-1` ruled and applied as a sidecar), **10.4** (per-dwelling assignment and emission), **10.9**
(paired Case A / Case B emission, §9.2). 🔴 **Everything still open needs a SIMULATED cell** — 10.3,
10.5, 10.6, 10.7, 10.8 and, since `FINDING 158`, **10.10** — and all of them wait on OpenUBEM `EU-04`.
Nothing in Step 10 is waiting on a 4J decision.

🔴 **Steps 8 and 9 are CLOSED and this step does not reopen them.** Step 8's definition of done closed
on 2026-08-25 (night) and was re-run rotated on 2026-08-26 under `D-S9-3`(a); Step 9's board is
**15 PASS / 3 FAIL / 1 NOT CHECKED** (`FINDING 149`). Their documents, their gates, their thresholds and
their published numbers are **read-only** from here. Step 10 is a new step with a new gate series
(`G10.x`), not a revision of Step 8.

🟡 **Step 10 completes when the OpenUBEM European-locations arc completes.** That arc is at
`EU-01`…`EU-03` complete and `EU-04`…`EU-10` in progress (MVP §9.7). Its remaining critical path is the
ERA5 weather acquisition and the contract freeze (MVP §12.8), plus the two items §4 and §6 below name.

---

## AIM

Re-test the Step 8 occupancy hypothesis on **observed European building stock** instead of TABULA
archetype boxes, with an **independent diary per dwelling unit**, so that the paper can say whether
Step 8's null is a property of occupancy or a property of the box that was simulated.

---

## 1. WHY THIS STEP EXISTS, STATED SO IT CAN BE ATTACKED

Step 8's result is a **null**. After the `D-S9-3`(a) rotated re-run: `FINDING 143` the peak claim does
not survive (ratio to between-diary spread 0.54 / 0.02 / 0.40), `FINDING 144` every annual median is
negative, `FINDING 145` the diurnal-shift sentence is withdrawn. **At `f = 1.00`, no occupancy claim
survives on either channel.** The one thing that survived is the **dwelling-class ordering**: the effect
is monotone in dwelling class in all three folds, `AB` above `MFH` above `TH`.

Step 8 could not have produced anything else, and this is not hindsight — it is the design:

* the unit was a TABULA archetype **box** (`D-S8-3`(a), equal-facade 1:1.5, sized to reproduce TABULA's
  wall area), not a real footprint;
* **one diary drove the whole cell.** Every dwelling-equivalent in an `AB` archetype shared one presence
  series;
* and `FINDING 134` measured the consequence directly: on annual heating **the effect is smaller than
  the between-diary spread in all three folds.**

A configuration in which every dwelling in a building carries the *same* presence series cannot express
inter-household diversity. Diversity is the mechanism the published European stock literature attributes
its 100–300 % dwelling-peak sensitivity to. The surviving dwelling-class ordering is the fingerprint of
that mechanism showing through a design that could not measure it.

### 1.1 The hypothesis, pre-declared before any Step 10 cell runs

> **`H10`** — at fixed `f`, the occupancy effect on building peak demand grows with `N_u`, the number of
> **independently diarised** dwellings in the building.
>
> **`H10₀`** (null) — it does not. The Step 8 null is a property of occupancy, not of the box.

🔴 **Both outcomes are publishable, and the null is the stronger paper.** Declaring `H10` here, in
writing, before a single Step 10 cell exists, is what separates this step from *re-running until a result
appears* — which is exactly what it would look like from outside, given that Step 8 has just returned a
null. The pre-declaration is the defence, and it only works if it is made now.

#### 1.1a 🔴 Sharpened 2026-08-26 (evening) after `RL28` was vetted. `H10`'s text is NOT edited.

`H10` above stands **verbatim**. What is added beside it is a **shape**, a **metric** and a **prior** —
all three recorded before any Step 10 cell exists. `VETTING_RL28_RL29.md` §2 carries the reasoning and
§1 carries what was rejected.

**The metric.** The `H10` test runs on the **coincidence factor**, not on an energy difference:

> `CF(N_u) = P_peak,building / sum over zones of P_peak,zone`, with the 99th-percentile hourly heating
> power reported beside it.

🔴 **This is the single most important change, and the reason is `FINDING 143`.** That claim died
because a peak effect was measured against a between-diary spread it could not beat (ratios 0.54 / 0.02 /
0.40). `CF` does not have that failure mode: it is dimensionless, bounded in `(0, 1]`, and in the
synchronised case it is **exactly 1 by construction**. The comparison is against a **constant**, not
against a spread. Annual EUI in `kWh/m2` is kept as a reported channel but is **not** where `H10` is
decided.

**The shape.** *"Grows with `N_u`"* is satisfied by almost anything. `H10` therefore also predicts the
functional form standard in load-aggregation theory:

> `CF(N) = g_inf + (1 - g_inf) / sqrt(N)`, one free parameter `g_inf`, fitted across the observed `N_u`
> and **reported with its residuals**.

This creates a **third distinguishable outcome** — monotone but not `1/sqrt(N)` — which is more
interesting than either of the original two.

🟢 **And the arithmetic of that form answers the obvious objection, in our favour.** The fraction of
the asymptotic effect reached at `N` is `1 - 1/sqrt(N)`, with `g_inf` cancelling:

| `N` | 2 | 4 | 6 | 10 | 20 | 50 |
|---|---|---|---|---|---|---|
| fraction of the asymptotic reduction reached | 29.3 % | **50.0 %** | 59.2 % | 68.4 % | 77.6 % | 85.9 % |

**Half of the entire effect is realised by `N = 4`.** Our one emitted `S1` layout carries
`units_per_floor = 5` (measured). So *"your buildings are too small for diversity to matter"* is refuted
by the theory itself — the small-`N` end is the **steep** end. ⚪ `RL28` claimed saturation
*"over 90 % by `N = 20` to `30`"*; that is **false on its own formula** (77.6 % and 81.7 %; 90 % needs
`N = 100`), and its consequent advice to sample for `N = 20`–`50` aims at the flat part.

**The prior, recorded before the run.** On heavy-mass European envelopes a conserved-mean redistribution
is attenuated by **92.4 % to 97.5 %** at the diurnal frequency (`tau = 50` to `150 h`, computed, not
quoted). **Annual heating EUI is therefore expected to stay null in Step 10 as well.** Writing that
down now is what makes a Step 10 annual null honest-and-boring instead of a surprise to be explained
away afterwards. 🔴 It also means **a Step 10 annual null is not evidence that Step 10 failed.**

### 1.2 🔴 What Step 10 may never do

**A Step 10 result does not rehabilitate a Step 8 claim.** `FINDING 143`, `144` and `145` withdrew
specific Step 8 claims; those stay withdrawn whatever Step 10 finds. A Step 10 finding is a finding about
**real stock with per-dwelling diaries**, and it must be written that way in every artefact. Gate
`G10.12` enforces the arithmetic half of this; the prose half is the author's.

---

## 2. WHAT CHANGES FROM STEP 8, AND WHAT DELIBERATELY DOES NOT

| Axis | Step 8 (closed) | Step 10 |
|---|---|---|
| Unit of simulation | TABULA archetype box, `D-S8-3`(a) | **observed footprint**, extruded to real storeys, shaded by real neighbours |
| Population | 102 archetypes × 5 `f` = 510 cells | OpenUBEM 510-cell contract **plus** real-stock neighbourhoods (Madrid / London / Bologna) |
| Diaries per building | **1** | **`N_u` independent**, one per dwelling (IMP §5.2, MVP §9.4) |
| Weather | `TMYx.2009-2023`, station chosen by measurement (`D-S8-4`, `FINDING 118`–`120`) | **ERA5 AMY per fold-year** (OpenUBEM `EU-07`) |
| Engine | local EnergyPlus via the Step 8 tooling | OpenUBEM 5-stage pipeline, one IDF and one E+ run per building |
| Injection formula | `φ_int(t) = (1−f)·3.0 + f·3.0·g(t)/mean(g)` | **unchanged, verbatim** |
| `f` set | `{0.00, 0.15, 0.30, 0.50, 1.00}` | **unchanged** |
| Conservation | annual mean exactly `3.0 W/m²` | **unchanged**, and now asserted **per zone as well as per building** (§9, `G10.13`) |
| Chaining rule | `independent`, seed 1 (decision 14, closed 2026-08-25) | **unchanged, by reference** (§5) |
| Schedule origin | rotated to midnight (`D-S9-3`(a), `G7.19` / `G8.17`) | **unchanged, inherited as a hard precondition** |

The treatment is carried across **verbatim** on purpose. If the injection formula, the `f` set, the
conservation property or the chaining rule moved, a Step 10 ≠ Step 8 difference would be uninterpretable.
The only intended differences are the **unit of analysis** and **diary diversity** — plus the weather
basis, which §3 shows is not a free change.

---

## 3. 🔴 THE WEATHER BASIS DIFFERS, AND THE DIFFERENCE IS LARGER THAN THE EFFECT BEING MEASURED

Step 8 runs on `TMYx.2009-2023` with the station selected by measurement against TABULA's own monthly
temperatures. Step 10 runs on OpenUBEM's ERA5 **actual-meteorological-year** files, one per fold-year.
These are different weather bases, and the size of that difference is already measured on the 4J side:

* `FINDING 120` — **the station alone is worth 5–11 % of heating demand.**
* `FINDING 133` — the entire occupancy channel is `+1.82 / −0.04 / +0.06 %` annual and
  `+6.38 / +4.54 / +3.96 %` peak, and `FINDING 143`/`144` then reduced even that.

**The basis change is worth more than the signal.** Any absolute comparison across the two steps would be
reporting the weather and calling it occupancy.

> **Pre-registered rule (scored by `G10.12`).** No artefact, table or figure ever places an **absolute**
> Step 8 EUI beside an **absolute** Step 10 EUI. What crosses between the steps is the
> **control-referenced relative delta** `(x_f − x_{f=0}) / x_{f=0}`, computed **within** each step's own
> weather basis, and even those are reported **side by side, never differenced**.

---

## 4. 🟢 **CLOSED 2026-08-26 — `D-S10-1` IS RULED. THE WEATHER YEAR IS PINNED AND THE OPENUBEM CONTRACT FREEZE IS LIFTED.**

| fold | pinned EPW year | measured share of diaries | basis |
|---|---|---|---|
| `es` | **2010** | **76.90 %** (14,718 / 19,140) | exact — `TRIM` value label + INE fieldwork window 1 Oct 2009 – 30 Sep 2010 |
| `uk` | **2014** | **58.11 %** (9,213 / 15,854) | exact, per diary — the delivered `dyear`, joined on `(serial, pnum, daynum)` |
| `it` | **2014** | 100 % after absorption; **≥ 72.8 %** exact | `meseri` 2/3/4 exact against the ISTAT window 1 Nov 2013 – 31 Oct 2014; `meseri=1` **absorbed** |

**Author's ruling, 2026-08-26 — option (A), the majority year per fold.** Three sub-rulings:
(1) option (A) overall; (2) `uk` pins to 2014 despite the 58/42 split, to keep one convention
across all three folds; (3) `it`'s straddling quarter is **absorbed into 2014, not interpolated**,
because the ISTAT daily-diary delivery ships no month field. 🟢 **The OpenUBEM
boundary-contract freeze (MVP §12.8, `FINDING EU-S2-03`) is LIFTED; Steps 10 and 11 are
unblocked.** Full record and every source: `../IMP/docs/2026-08-26_D-S10-1_the-weather-year-is-recoverable.md` §6.

### 4.0.1 🔴 What the ruling was applied to — a SIDECAR, never the corpus

`tools/4thJ_step10_weather_year.py` writes `outputs_step10/weather_year_ruling.json` (the
fold → `--year` pinning OpenUBEM's converter consumes) and `diary_year_{es,uk,it}.parquet`
(per-diary year **and the basis for it**, `exact` or `absorbed`). 🔴 **`harmonised_*.parquet`
was NOT edited** — directive 2 requires the enrichment not invalidate Step 2 gates, and an edit
in place would move them and, downstream, the frozen `corpus_md5 ca89d229…`. Gate **`W10.1`**
proves it by hashing the three inputs before and after.

Eight gates, **8 PASS / 0 FAIL**, and 🔴 **four were seen felling on purpose** before the
outputs were trusted: flipping the `es` map fells `W10.3`; breaking the `uk` join key fells
`W10.4`; flipping the `it` map fells `W10.6`; mis-pinning `uk` to the minority year 2015 fells
`W10.7`. Report: `outputs_step10/weather_year_report.txt`.

⚪ **One number to carry into the methods, not to hide:** `it`'s absorbed quarter is
**10,160 of 38,260 diaries (26.6 %)** — those diaries are *assigned* 2014, not *measured* as
2014. `es` and `uk` have no absorbed diaries at all.

---

## 4.b ⚪ SUPERSEDED, KEPT AS THE RECORD — the decision as it stood before the ruling

`FINDING EU-S2-03` (MVP §12.12) is a decision request pointed at this project:

```
fr  diary_window 2023-01-01/2023-12-31   RULED_PINNED
es  diary_window None                    RULED_NOT_PINNED   era5 2009-01-01/2010-12-31
uk  diary_window None                    RULED_NOT_PINNED   era5 2014-01-01/2015-12-31
it  diary_window None                    RULED_NOT_PINNED   era5 2013-01-01/2014-12-31
```

An EPW is one year; each fold's window is two. OpenUBEM's converter **refuses to default** — without an
explicit `--year` it prints `YEAR_NOT_RULED <fold> <window>` and writes nothing; `--all-years` emits one
EPW per complete calendar year so neither is overwritten. The ruling is explicit that *"choosing which
year a campaign cell uses is a diary question, and the diary is GSSCanada's"* — the same boundary §12.11
draws for the held-out fold, applied to time instead of geography.

### 4.0 🟢 SUPERSEDED IN PART, 2026-08-26 (night) — **ROUTE (a) WAS TRIED AND IT WORKED**

🔴 **§4.1 below is correct about the HARMONISED corpus and wrong as a description of what is
knowable.** The raw deliveries were read on 2026-08-26 and **all three folds' calendar years are
recoverable** — `es` and `uk` exactly, `it` with one straddling quarter. `es` 2010 **76.8 %**,
`uk` 2014 **58.1 %** (from the delivered per-diary variable `dyear`), `it` 2014 **≥ 72.8 %**.
⚪ 🔴 **Trap, filed:** the Italian delivery has a column named `anno` and it is a constant
`2013` on all 1,077,657 rows — a wave stamp, **not** a diary year.

🟢 **RULED the same day — see §4 above.** The author took option (A), the majority year
per fold. This paragraph is kept only to show the decision was answerable before it was answered.
Full record, with every source and count: **`../IMP/docs/2026-08-26_D-S10-1_the-weather-year-is-recoverable.md`**.

### 4.1 🔴 Measured on the artefact, 2026-08-26 — the current corpus cannot answer it

`harmonised_{es,uk,it}.parquet` (41 columns) was read directly rather than reasoned about:

| fold | `wave` | `strat_season_raw` |
|---|---|---|
| `es` | `2009-2010`, single value, 446,547 rows | quarters `1`–`4` |
| `uk` | `2014-2015`, single value, 567,381 rows | **months `1`–`12`** |
| `it` | `2013-2014`, single value, 1,010,140 rows | quarters `1`–`4` |

**No column resolves the calendar year.** `wave` carries the two-year window and nothing finer; the season
field is a quarter for `es`/`it` and a month for `uk`, and a month cannot separate 2014 from 2015. So
`D-S10-1` is **not answerable by measurement on the harmonised corpus**, and the three options are:

* **(a) recover the collection year from the Step 1 raw deliveries.** INE `datos_emptiem0910`, UKDS SN
  8128, ISTAT *Uso del Tempo* 2013-14 — the raw record layouts may carry a diary date that Step 2 did not
  keep. Cheap, and the only option that produces a **fact** rather than a convention.
* **(b) declare the year a design factor** and run both, doubling the weather axis (not the campaign).
  The one option that cannot invent an answer.
* **(c) an author ruling** on a documented basis (e.g. the year carrying the larger share of fieldwork),
  recorded as a convention and carried in the caveat register.

**Recommendation: try (a) first, fall back to (b).** (c) only if (a) fails and (b) is unaffordable.

🔴 **This blocks more than Step 10.** MVP §12.8 lists the contract freeze as waiting on the weather rows,
and `FINDING EU-S2-03` is precisely the reason a fold can remain `RULED_NOT_PINNED` **after a technically
successful acquisition**. Until `D-S10-1` is ruled, `es`/`uk`/`it` cannot each be reduced to one EPW, and
the OpenUBEM boundary contract cannot be signed. 🟢 **— RESOLVED 2026-08-26, see §4 above.**

---

## 5. 🟢 **CLOSED 2026-08-26 (night) — WORK ITEM 10.1 IS FILED. THE `f > 0` BLOCK IS LIFTED BY REFERENCE.**

🟢 **The closure notice exists: `Step10_docs/docs/2026-08-26_10.1_chaining-closure-notice.md`.**
It carries all four artefacts §10.2 item 6 asked for — the frozen rule text (`independent`, seed 1,
`rho = 0`, year 2017, 8,760 hourly values, `diary_origin_hour = 4` **rotated to midnight**), the seed
policy (production seed **1**; experiment seeds **11/22/33/44/55**, a pre-registered minimum the runner
refuses to go below), the implementing script with `FINDING 147` attached to it, and the spread table
re-measured on the **rotated** schedules. 🔴 **It also withdraws one sentence:** `FINDING 136`'s
*"17–60×"* occupancy-to-convention comparison does not survive the rotation (9.4× / 0.2× / 22.6×) and
must not be repeated — the claim decision 14 rests on is `G7.18`'s trigger, which is missed by two
orders of magnitude in every fold (0.2892 / 0.1936 / 0.0285 % against 25 %).

⚪ `Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md` §10 was de-staled the same night. **MVP §12.11
is on the OpenUBEM side and is theirs to correct**, on receipt of the notice.

---

## 5.b ⚪ SUPERSEDED, KEPT AS THE RECORD — the item as it stood before the filing

Two live OpenUBEM artefacts are **stale** on this point:

* `IMP_step8/4thJ_08_bemSimulation_IMP.md` §10 — *"the **only remaining blocker** of the OpenUBEM European
  campaign … It gates **only the `f > 0` occupant cells (408 runs, Q4)**"*;
* MVP §12.11 receiving step 3 — *"`schedule_status` already marks the four non-zero levels
  `BLOCKED_CHAINING_RULE` — that block is D-EU-09, upstream in Step 7, and it is not OpenUBEM's to lift."*

**It was lifted on 2026-08-25 (night).** `FINDING 136`: 9,000 additional runs measured the entire chaining
convention at **0.178 / 0.075 / 0.239 %** of peak demand against `G7.18`'s **25 %** trigger; the seed
spread beat the rule spread on every metric in every fold; the occupancy effect was **17–60×** the
convention's whole range. The author ruled the same night: **decision 14 is closed — `independent`,
seed 1, adopted as the standard convention for every published Step 8 and Step 9 dataset, with the
empirical null itself as the deliverable.** No re-run, no pipeline change.

**Work item 10.1 is therefore a closure notice, not an experiment.** IMP §10.2 item 6 lists exactly what
is owed back — the frozen rule text, the seed policy, the implementing script, the spread table — and all
four already exist (`tools/4thJ_step8_chaining.py`; `FINDING 136`'s table; `FINDING 147` records that this
script bypassed the emitter and that its first rotated re-run returned bit-identical to the superseded
one, which must travel with it). Filing it lets the OpenUBEM director lift the `f > 0` block **by
reference**, unblocking Q4's 408 runs. 🟢 **Done 2026-08-26 (night); see the header of §5.**

---

## 6. 🔴 THE PER-DWELLING CONFIGURATION IS GEOMETRY-LIMITED, AND THE LIMIT IS SEVERE

`S1` ran on 2026-08-25 under ruling `D-EU-04-H`(H1) and measured the yield rather than selecting on it.
Of the 12 ladder buildings, **1** emitted a dwelling layout; **8** were `NON_CONVEX_FOOTPRINT` refusals
and **3** were `NARROW_FOOTPRINT_LT_8M` fallbacks. Across the full French layout-ready set the census is
**18 emitted of 297**, with **256 of 297** footprints non-convex or holding a courtyard.

`H10` needs `N_u ≥ 2` buildings. This is the constraint that decides whether `H10` is testable at all, and
it must be designed for rather than discovered:

1. **Two populations, scored separately and never pooled.**
   * **Arm D** — dwelling-partitioned buildings, `N_u ≥ 2`, one independent diary per dwelling. This is
     where `H10` is tested.
   * **Arm F** — `one_zone_per_floor` fallbacks, effectively `N_u = 1`. This is the **Step 8
     configuration on real geometry**, and it is a second control worth having: it separates
     *real footprint* from *diary diversity* as explanations of any Step 10 ≠ Step 8 difference.
   Scored by `G10.9`.

2. **🔴 Arm D is selected on footprint convexity**, which correlates with construction epoch and typology.
   It is **not a random sample of the stock**, so **no stock-level EUI may be quoted from Arm D** — only
   within-arm, control-referenced deltas. Also scored by `G10.9`.

3. **🔴 The two arms are not yet comparable in vertical extent.** The single `S1` dwelling-level run was
   *a single floor plate of 5 dwellings* (`zone_count = 5`, `units_per_floor = 5`), not the 6-storey /
   28-dwelling stack, while all 11 fallback runs were full stacks (`zone_count = observed_storeys`).
   MVP records this explicitly: the dwelling-level path *"must never be quoted as 'a 6-storey
   dwelling-partitioned building runs'"*. **Work item 10.3 is full-stack parity**, and until it lands
   `H10` cannot be tested, because `N_u` and vertical extent would be confounded.

4. **🔴 Layout success is CRS-dependent.** `generate_european_dwelling_layout` rotates about the literal
   coordinate origin (`openubem/geometry/european_residential.py:504`) while
   `audit_european_floor_partition` compares against an **absolute** `topology_tolerance_m2 = 1e-8`
   (`:643`), so rotation noise scales with distance from `(0,0)`. The same building emits cleanly in
   `EPSG:32631` and fails `AREA_GAP` + `OUTSIDE_FOOTPRINT` in `EPSG:2154` at an `area_error_fraction` of
   **5.09e-12**. A census in Lambert-93 would have reported near-zero emitted layouts for the same corpus.
   Native CRS, no reprojection, **declared in the manifest and asserted** — `G10.10`.

   🔴 **Restated 2026-08-26 (evening): the recorded arithmetic does not close, and `G10.10`'s
   target moves because of it.** The failing building is `BATIMENT0000000240879449_part0`, footprint
   **544.206 m²** (`s1_smoke_manifest.csv`). At an error fraction of `5.09e-12` the implied absolute
   gap is **2.77e-9 m²** — *inside* the `1e-8 m²` tolerance, which would only be crossed above
   **~1 965 m²**. So the refusal is **not** explained by "the absolute tolerance is too tight for the
   plate": either `area_error_fraction` is not `|dA|/A`, or the binding refusal is `OUTSIDE_FOOTPRINT`,
   a containment test rather than an area test. **What survives is the code fact** — rotation about
   the literal origin at `~852000 / 6519000` — and that is what `G10.10` tests: **the rotation origin,
   not the tolerance units.** The `5.09e-12` / `1e-8` pairing must not be repeated as a causal
   statement until it is re-measured. (`VETTING_RL28_RL29.md` §1.6.)

5. 🔴 **CORRECTED 2026-08-26 (evening) — the 173-vertex `EPLUS_FATAL` is a stale blocker. It is
   gone, and its diagnosis was false.** This document previously repeated the record carried in
   `OpenUBEM_debug_References.md` ch.1 and `MVP_european_locations.md` §EU-04: one `S1` building
   `EPLUS_FATAL` on a 173-vertex exterior ring, *"against the IDD's ~120-vertex `BuildingSurface:Detailed`
   limit"*. Both halves fail on measurement.

   * **The limit does not exist.** In `EnergyPlusV22-1-0` and `V24-2-0`, `BuildingSurface:Detailed`
     carries `\extensible:3`, `\min-fields 20` and **no `\max-fields`**, and the IDD's own note reads
     *"shown with 120 vertex coordinates — **extensible object**"*. 120 is what is printed, not a
     ceiling.
   * **The failure no longer reproduces.** `EPLUS_FATAL` appears **nowhere** in the EU-04 evidence tree.
     `s1_smoke_manifest.csv`, regenerated **2026-08-26 12:10**, reports **12 of 12 `EPLUS_COMPLETED`**,
     and `BATIMENT0000000240877527_part0` ends *"Completed Successfully — 0 Severe Errors"* in **all
     three** campaigns (`s1_smoke`, `s2_campaign`, `s2_campaign_v2`). The layout axis is unchanged
     (8 refused / 3 fallback / 1 emitted), so this is the same 12 buildings, re-run.

   ⚪ **`RL29` proposed a design change on the strength of the false half** — RDP simplification at
   `epsilon = 0.15 m` applied to every cadastral polygon. Adopting it would have altered the geometry of
   the whole corpus to fix a defect that is already gone. **Rejected**; see `VETTING_RL28_RL29.md`
   §1.4–§1.5. The general rule stands unchanged and is not weakened by this correction:
   **refusals are counted and classified, never silently dropped from a denominator.**

6. 🔴 **`H10` is tested within a footprint, not across footprints.** Buildings that happen to carry
   different `N_u` also differ in volume, envelope area and shape factor, so a cross-building comparison
   confounds **diversity** with **geometry**. Every Step 10 building therefore runs **twice** at each `f`:

   | Case | Diaries | What it holds fixed |
   |---|---|---|
   | **A — synchronised** | one diary, replicated to all `N_u` zones | everything except diversity; `CF = 1` by construction |
   | **B — independent** | `N_u` independently sampled diaries | same footprint, archetype, weather, `f`, seed policy |

   The effect is `delta_div = Metric(B) - Metric(A)`, **within footprint**. 🟢 The pairing also makes
   `H10` testable on **Arm F** geometry, which matters because Arm D is 18 buildings of 297. Scored by
   `G10.20`; the cost is one extra run per cell and it is the cheapest control in the step.

---

## 7. FRANCE IS NOT A FOLD

Lyon is OpenUBEM's fourth European site. France appears in the 4J corpus table only as a candidate under
author decision 6, and the scope amendment of 2026-08-15 fixed the corpus at **three countries, `es` /
`uk` / `it`**. There is no French HETUS fold, therefore no French held-out fold, therefore no French
diary.

**France enters Step 10 in exactly one way: as `FR-B`, a physical baseline with no occupant schedule, on a
separate manifest** (MVP §10.3). Its cells never enter a 4J denominator and never carry a `f > 0` value.
Scored by `G10.11`.

---

## 8. THE BOUNDARY CONTRACT, AND WHAT 4J MAY NOT DO

MVP §12.11 fixes the hand-off. **Exactly four artefacts cross**, and the receiving order is not
interchangeable:

1. **Verify the freeze before running anything** — re-run `validate_campaign_cells` on the contract's own
   `cells` array: 510 rows, 510 unique ids, 102 at each `f`, 102 archetypes, ordered levels with the
   `f = 0` control first, fold set exactly `{es, uk, it}`. A contract that does not re-validate has been
   edited after signature.
2. **Read the 22-entry caveat register before reading any number** — specifically C-01, C-03 and C-09, the
   end-use, geometry and vacuity limits.
3. **Run the `f = 0` controls first.** Every cell carries `control_cell_id`.
4. **Treat any `RULED_NOT_PINNED` fold as unrunnable, not runnable-with-a-substitute.** Its `epw_path` is
   unresolved deliberately (see `D-S10-1`, §4).

🔴 **4J must not patch IDFs after generation.** An edited IDF silently invalidates `idf_sha256` and every
dependency digest computed from it. A wrong cell is a **defect report against the specification**, never a
post-generation edit.

🔴 **OpenUBEM manifests carry `held_out_country = null` by design** — an honest null, because OpenUBEM must
not infer the fold from a country filename. **Step 10 owns fold assignment**, and `G10.8` scores it
against 4J's own Step 7 provenance, locating each diary **by content** among the bundles on disk exactly
as `G8.16` did — never against the cell's filename and never against OpenUBEM's null.

---

## 9. PER-DWELLING INJECTION, AND THE CONSERVATION PROPERTY THAT MUST NOW HOLD TWICE

Arm D assigns `N_u` **independent** diaries drawn from the held-out fold's Step 7 pool, one per dwelling
zone, with the seed recorded per `(building_id, unit_index)`. `φ_int` is emitted per zone.

Step 8's conservation clause said *annual mean exactly `3.0 W/m²`*. With `N_u` series per building that
clause is ambiguous, and the ambiguity is exactly the shape of `FINDING 132` — the pre-registered
conservation *held in the generator and not in the artefact*. Step 10 fixes the ambiguity in advance:

> The annual mean of `φ_int` is exactly `3.0 W/m²` **per zone** *and* **per building** at every `f`,
> asserted on the **emitted CSV on disk**, with the numeric bound derived from the write format —
> not asserted in the generator.

Scored by `G10.13`. Held-out-fold correctness (`G10.8`) applies **per dwelling**: no dwelling in a fold's
campaign may carry a diary from that fold's held-out records.

### 9.1 🟢 BUILT 2026-08-26 (night, last) — work item 10.4

`tools/4thJ_step10_assign.py`. **297 buildings → 1,576 dwellings → 7,880 emitted hourly CSVs.**
`G10.13` **PASS** on **9,365** rows (7,880 per-zone + 1,485 per-building, area-weighted);
`G10.8` **PASS**, 0 unlocatable and 0 wrong-fold of 1,576; `G10.9` **PASS**, 0 buildings
carrying both arms; `G10.19` **`NOT_EVALUABLE`** — and that is the gate working. Battery
**6 of 6**. ⚪ This is the tool, not a campaign: no EnergyPlus was run and none is owed here.

🔴 **`G10.19` reproduces §6's severity from the artefact rather than the prose.**
Qualifying buildings — Arm D with `N_u ≥ 2` — are **es 9 · uk 5 · it 3** against the **30 per
fold** `H10` needs. The whole layout census offers **18** Arm D buildings in total. **The gate
says so before a campaign is built, not after.**

🔴 **The `G10.13` bound is TIGHT, not slack.** Largest deviation anywhere is
**1.347e-10 W/m²** against a bound of **1.5e-10** — **90 % of the allowance used**. The bound
is derived from the `%.10f` write format, never chosen to clear the result.

**Three decisions the item had to take, recorded because none is obvious:**

1. 🔴 **The arm comes from `zone_source`, NEVER from `zone_count`.** A building with
   `zone_count = 4` under `FALLBACK_ONE_ZONE_PER_FLOOR` is four **storeys**, not four
   dwellings; assigning it four independent diaries would **manufacture the exact diversity
   `H10` exists to test for**. The battery demonstrates it: read the arm from `zone_count` and
   `G10.19` flips `NOT_EVALUABLE → PASS` on a population made of storeys.
2. **Arm F gets ONE diary for the whole building**, repeated across its storey zones — the
   fallback spatially averages non-coincident gains by construction (`G10.22` calls it a lower
   bound), and pretending each storey is an independent household would hide the bias that
   makes it one. Measured: **0** Arm F buildings carry more than one distinct diary, and
   **0** of the 18 Arm D buildings repeats a diary across its own dwellings.
3. ⚪ **Zone areas are `footprint_area_m2 / zone_count` — an ASSUMPTION, not a measurement.**
   The real per-zone areas arrive with the dwelling layout. Declared because equal areas make
   the area-weighted arm of `G10.13` true by symmetry, which is why the battery includes a
   very-unequal-areas case.

🔴 **Three defects the battery found in the tool's own first draft**, each recorded in
`impl/2026-08-26_work-item-10.4_per-dwelling-assignment.md`: `G10.8` returned **PASS on an
empty population** (both gates now return `NOT_EVALUABLE` instead); the perturbation that
exposed it was itself **badly designed** — it *removed* the gate rather than testing it, and
was replaced by a genuine cross-fold mislabel; and **globbing the Step 7 schedules directory
picked up the `leg4_*`, `_cal<year>` and `perturb_*` bundles** — the reader refused
`perturb_hours_8759`'s short year, and the bundle set is now read from the **campaign's own
`schedule_bundles` field**, because `perturb_null`'s manifest is indistinguishable from a
production one.

⚪ **Reduced in flight, declared not discovered.** 7,880 hourly CSVs is 2.6 GB per run and the
battery runs it six times, so each file is **read from disk by `G10.13` at the moment it is
written** (`V10.h` intact) and then removed unless it is in the retained sample. **What is
dropped is the artefact, never the measurement.** 35 CSVs kept; the tree is 18 MB.

⚪ Exercised on the **real** OpenUBEM layout census (297 rows, its own zone counts, footprint
areas and refusal mix) with **one declared change**: the country label, because that census is
French and **France is not a fold** (§7). When the 4J building table arrives with 10.3 it
replaces the exercise table and **nothing in the tool changes**.

### 9.2 🟢 BUILT 2026-08-27 — work item 10.9, the paired emission

`tools/4thJ_step10_paired.py`. Every building emitted **twice at every `f`** — Case A synchronised,
Case B independent, same footprint, same zone areas, same arm, same fold, same seed stream.
**297 buildings → 3,152 paired rows → 15,760 emitted hourly CSVs → 2,970 cells → 1,485 `delta_div`
rows, 0 refused.** `G10.20` **PASS**; `G10.13` **PASS** scored **per case**; `G10.8` **PASS**
(3,152 dwellings); `G10.9` **PASS**; `G10.19` **`NOT_EVALUABLE`** at es 9 · uk 5 · it 3, unchanged
from 10.4 as it must be; `G10.21` **`NOT_EVALUABLE`** with its population named — *simulated Step 10
cells, size 0*. `W10.11` **PASS**: the Arm D half of Case B reproduces 10.4's shipped
`assignment_table.csv` at **143 of 143 rows, 0 differing**, read off that artefact rather than
asserted from both tools calling one function.
Battery **10 of 10**, and the **null case fells nothing** — `G10.20` seen failing on three distinct
clauses, `G10.13` on two, `G10.8` on two, `W10.9` on its rewritten arm, `G10.19` flipping
`NOT_EVALUABLE → PASS` on a population of storeys.
Record: `impl/2026-08-27_work-item-10.9_paired-case-a-case-b.md`.

🔴 **THREE FINDINGS, AND EACH ONE NARROWS WHAT `G10.21` AND 10.10 CAN BE.**

* **`FINDING 158` — on the emitted `phi_int` channel the coincidence factor is exactly 1 by
  construction.** **1,450 of 1,450** Case B cells with `N_u ≥ 2` return `CF_phi = 1` to 1e-12, and every
  one of them holds at least one hour where **all** its zones sit at their own maximum — **minimum 396
  such hours** in the worst cell. Every Step 7 presence series reaches 1.0, so independent households
  still coincide. **Diversity cannot lower the DRIVER peak**; any `CF < 1` in Step 10 must come from the
  thermal response, so `G10.21` **cannot be discharged by any pre-simulation artefact**. 🔴 **The
  pre-registered consequence for 10.6, written before it runs: `CF_A = CF_B = 1.000` on simulated power
  would be a `NOT_EVALUABLE`, not a null.** §1.1a's *"comparison against a constant"* stands; what is
  added is that **the constant is not evidence**.
* **`FINDING 159` — the 99th-percentile hourly power equals the peak in 2,970 of 2,970 cells** (2,376 of
  2,376 among `f > 0`). Presence saturates at 1.0 for far more than 1 % of the year, so `q99 = max`
  exactly. Before simulation, quoting `CF` and `q99` side by side is quoting one number twice.
* **`FINDING 160` — `delta_div` on this channel is a statement about WHICH diary Case A replicates.**
  At `f = 1.00`: median **0.73 %** (Arm D, n = 17) and **1.22 %** (Arm F, n = 273) against a Case-A
  choice spread of **31.77 %** and **30.00 %** — ratios **0.198** / **0.295**, and **0 of 290 rows** in
  either arm beat the spread of the parameter that was free. `FINDING 143`'s shape, caught before
  publication; the ratio ships as its own column.

🔴 **The battery felled a guard of ours before the guard could ship.** The first `W10.9` scored
`G10.21`(ii) literally — Case A's `CF_phi` must be 1 — and the battery's `case_a_independent` case, the
exact harness defect that clause exists to catch, came back **PASS**. A guard whose discriminator is
constant in the ground truth is not a guard. `W10.9` now scores **series identity** (sha256 of the
emitted files, taken before reduction); the `CF = 1` arm is retained, reported, and stamped
**`CARRIED, NOT SCORED`** in the artefact so it can never be quoted as evidence of correct
synchronisation. `W10.12` publishes the degeneracy as a measurement.

🔴 **The reading 10.9 had to take, recorded because two documents pull.** 10.4 ruled *"Arm F gets one
diary for the whole building"*; §6.6 says *"every Step 10 building therefore runs twice"*. **10.4
governs the PRODUCTION assignment and is untouched** (`W10.11` is the proof); **10.9 is a paired
probe**, and on Arm F its zones are **storeys**, so its `delta_div` measures the averaging bias
`G10.22` labels rather than dwelling diversity. Every row carries `zone_semantics`; `G10.19` counts
Arm D only; `G10.9` keeps the arms apart. **An Arm F delta is never an `H10` dwelling result.**

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. `H10`'s text unedited, no `G10.x`
threshold moved, no gate loosened — `W10.9` was **tightened**.

---

## 10. WORK ITEMS

| # | Item | Depends on | Simulation? |
|---|---|---|---|
| **10.1** | ✅ **DONE 2026-08-26 (night)** — **chaining closure notice FILED**: `docs/2026-08-26_10.1_chaining-closure-notice.md`, all four owed artefacts with md5s, `FINDING 136`'s `17–60×` sentence withdrawn (§5) | nothing | no |
| **10.2** | ✅ **DONE 2026-08-26 (night)** — recovery (a) succeeded on all three folds and the author RULED: **`es` 2010 · `uk` 2014 · `it` 2014**, applied as a sidecar, 8 gates PASS / 4 seen felling; the OpenUBEM contract freeze is **LIFTED** (§4) | nothing | no |
| **10.3** | **Full-stack parity** — Arm D and Arm F at equal vertical extent (§6.3) | OpenUBEM `EU-04` | smoke only |
| **10.4** | ✅ **DONE 2026-08-26 (night, last)** — `tools/4thJ_step10_assign.py`; 297 buildings → **1,576 dwellings** → **7,880 emitted CSVs**; `G10.13` **PASS** on 9,365 rows (7,880 zone + 1,485 building), `G10.8` **PASS** 0/1,576 wrong-fold, `G10.9` **PASS**, `G10.19` **`NOT_EVALUABLE`** (es 9 · uk 5 · it 3 against 30); battery **6 of 6** (§9) | 10.1, Step 7 pools | no |
| **10.5** | **`f = 0` control campaign** on real stock — Q1 → Q2 → Q3, plus `FR-B` on its own manifest | 10.2, 10.3, contract freeze | yes |
| **10.6** | **Injected campaign** `f ∈ {0.15, 0.30, 0.50, 1.00}`, dependency-enforced `Q3 → audit → Q4` | 10.4, 10.5 | yes |
| **10.7** | **`H10` test and aggregate** — Arm D and Arm F reported separately | 10.6 | no |
| **10.8** | **Gate board, mutation battery, dossier** — every `G10.x` seen failing its designated mutation | 10.7 | no |
| **10.9** | ✅ **DONE 2026-08-27 — the EMISSION half.** `tools/4thJ_step10_paired.py`; 297 buildings → **3,152 paired rows** → **15,760 emitted CSVs** → 2,970 cells → **1,485 delta_div rows, 0 refused**; `G10.20` **PASS** (0 missing partners, 0 geometry mismatches, 0 cross-building rows, 15,760 files scanned), `G10.13` **PASS** per case, `W10.11` **PASS** 143/143 against 10.4's shipped table; battery **10 of 10** with the null case moving nothing. 🔴 The **simulated** half stays with 10.5 / 10.6 (§9.2) | 10.4 | yes (owed by 10.6) |
| **10.10** | 🔴 **`CF` and the `sqrt(N)` fit** — coincidence factor, 99th-percentile power, one-parameter fit reported with residuals (§1.1a). 🔴 **`FINDING 158`/`159` removed the early route: on the emitted schedules `CF_phi` is 1 in 1,450 of 1,450 cells and `q99` equals the peak in 2,970 of 2,970. This item cannot start before simulated cells exist** | 10.9, **10.6** | no |
| **10.11** | ⚪ **Rotation-origin fix, upstream** — centroid-translate before rotating in `european_residential.py`; an OpenUBEM item, requested not implemented by 4J (§6.4) | nothing | no |

**Order is enforced, not suggested.** MVP §10.6: the control-audit job must exit non-zero if any Q3 cell
or gate is missing, so the injected array never becomes eligible. Placing all rows in one array is
explicitly weaker — an array scheduler may start `f > 0` before the controls finish.

---

## 11. WHAT THIS STEP CANNOT DELIVER, STATED NOW RATHER THAN LATER

* **No measured-accuracy claim.** There is no metered data for these neighbourhoods. `G10.1`–`G10.4` are
  reproducibility tripwires against an independent re-run, `D-S8-1`(a) extended verbatim — the same
  `FINDING 44` inversion Step 8 had to correct.
* **No published-band verdict.** `G10.7` is **INFO permanently**; `D-S8-5` item 1 ruled that no numeric
  EUI band is created anywhere in this project, and Step 10 does not create one.
* **No stock-level EUI from Arm D** — the arm is selected on footprint convexity (§6.2).
* **No per-dwelling prediction** — inherited from `G9.13` into Step 11 as `G11.13`.
* **Nothing that reinstates a Step 8 claim** that `FINDING 143`/`144`/`145` withdrew (§1.2).
* **No effect magnitude taken from the literature.** `RL28` states the heating-peak reduction as
  2–6 % in one section and 5–15 % in another; neither is pre-registered. Step 10 measures it.
* **No numeric fallback-bias figure.** `RL29`'s −5…−15 % annual and −10…−25 % peak rest on a
  self-refuting citation (`[R2]`). Only the **direction** is carried — Arm F under-predicts, so an
  Arm F stock total is a **lower bound** (`G10.22`).
* **`G8.15` is an open FAIL on the OpenUBEM side** (MVP §12.5, untriaged warnings). `G10.15` inherits it
  **as open**, and Step 10 does not report it as clean because it changed engines.

---

## PROGRESS LOG

### 2026-08-26 — planned

Step 10 and Step 11 authored after the author fixed the scope: Steps 8 and 9 are preserved as a closed
chapter and the OpenUBEM integration becomes Steps 10 and 11 **inside paper 4**, completing when the
OpenUBEM European-locations arc completes.

Two facts were **measured rather than assumed** while writing this document:

* 🔴 **`D-S10-1` is not answerable from the harmonised corpus.** `harmonised_{es,uk,it}.parquet` carries
  `wave` (`2009-2010` / `2014-2015` / `2013-2014`, one value each) and `strat_season_raw` (quarter for
  `es`/`it`, month for `uk`) and **no calendar-year column** (§4.1). Read from the parquet schema and
  value counts, not from a schema document.
* 🔴 **`IMP §10` and MVP §12.11 step 3 are stale** — both still name the diary-day chaining rule as the
  European campaign's only remaining blocker, and the author closed it on 2026-08-25 (night) with
  `FINDING 136`'s null as the deliverable (§5). Work item 10.1 exists to lift it by reference.

### 2026-08-26 (evening) — `RL28` and `RL29` returned, vetted, and partly rejected

Full record: `../DeepResearchPrompts/VETTING_RL28_RL29.md`.

🔴 **The round's most valuable output was not the literature. It was that vetting it re-measured two
blockers this project had written down, and both were wrong.**

* **The 173-vertex `EPLUS_FATAL` is dead** — `EPLUS_FATAL` appears nowhere in the EU-04 evidence tree,
  and the S1 manifest regenerated 2026-08-26 12:10 reports **12 of 12 `EPLUS_COMPLETED`**. §6.5 corrected.
* **Its diagnosis was false too** — there is no 120-vertex `BuildingSurface:Detailed` limit; the object is
  `\extensible:3` with no `\max-fields` in both installed IDDs. `RL29` returned our own prompt's figure
  rated **Tier 1, confidence H, "read full text"**. Laundered, not verified.
* **The CRS arithmetic does not close** — 544.206 m² at a fraction of 5.09e-12 is a 2.77e-9 m² gap,
  *inside* the 1e-8 tolerance. `G10.10` retargeted to the rotation origin (§6.4).

Three things were **accepted on their own logic** and are now in the design: the paired within-footprint
Case A / Case B control (§6.6), the coincidence factor as `H10`'s decision metric (§1.1a), and the
`1/sqrt(N)` shape as a sharper pre-registration. 🔴 **`H10`'s pre-declared text was not edited** —
a hypothesis rewritten after commissioning literature that predicts its outcome is indistinguishable
from moving the goalposts.

Rejected and recorded: the RDP remedy, the 120-vertex limit, `RL28`'s saturation percentages, every
fallback-bias number resting on `[R2]`, and `Iseri et al. (2026)` cited back to us as evidence for our
own design.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No Step 8 or Step 9 threshold moved, no
checker edited, no `G8.x` or `G9.x` gate ID reused — Step 10 opens a new `G10.x` series and states its
inheritance per gate.


### 2026-08-26 (night) — 🟢 work item 10.1 is DONE: the chaining closure notice is FILED

`Step10_docs/docs/2026-08-26_10.1_chaining-closure-notice.md`. **A filing, not an experiment** — all four
artefacts §10.2 item 6 asks for already existed; what was missing was the document that lets the OpenUBEM
director lift `BLOCKED_CHAINING_RULE` on **408 runs (Q4)** by reference instead of re-deriving the answer.

**The four, with md5s recorded in the notice:**

1. **The frozen rule text** — `independent`, `rho = 0`, seed 1, year 2017 Sunday-start, 8,760 hourly
   values, `interpolate_to_timestep = No`, stratum key backed off one field at a time with
   `strat_day_type` **never** dropped. 🔴 `diary_origin_hour = 4` **with**
   `rotated_to_midnight = true` is the day-boundary convention and the two must be read together — a
   consumer who re-derives from raw diaries without rotating disagrees with the shipped bundles by four
   hours (`FINDING 141`).
2. **The seed policy** — production seed **1**; experiment seeds **11/22/33/44/55**, a pre-registered
   minimum the runner *refuses* to go below. Checkable in the artefact, not only in prose:
   `injected_campaign.json` names its bundles `leg5_{es,uk,it}_independent_seed1`.
3. **The script** — `tools/4thJ_step8_chaining.py` (`cab2417b…`), with **`FINDING 147` attached to it and
   not separable from it**: it once bypassed the emitter and its first rotated re-run came back
   bit-identical to the superseded campaign across 9,000 runs. The class of defect is the point — *a
   re-run that reproduces the old answer exactly is evidence the fix did not reach the tool.*
4. **The spread table** — re-read from `chaining_step8.json` (`rotated_to_midnight: true`), not
   transcribed from the earlier prose. Peak spread **0.2892 / 0.1936 / 0.0285 %** against `G7.18`'s
   **25 %**; every varying metric returns **NOISE DOMINATES** with ratios 0.075–0.482;
   `trough_aggregate_w` is **DEGENERATE** in all three folds and says so rather than reporting a vacuous
   ratio.

🔴 **One sentence was withdrawn in the filing.** `FINDING 136`'s *"the occupancy effect is
17–60× the convention's entire range"* does not survive the rotation — the multiples are **9.4× / 0.2× /
22.6 ×**, and in `uk` the occupancy channel is now the *smaller* of the two. 🟢 That does not
weaken decision 14: both quantities sit below the between-diary spread in `uk`, so **neither is
measurable there**, and the claim the decision rests on is `G7.18`'s trigger, which is missed by two
orders of magnitude in every fold. The notice says this in place rather than quietly dropping the number.

🟢 **The four constraints §10.3 inherited from the pre-registration are each discharged in the
notice**, against the **rotated** campaign (440 cells, 4,048 runs, **31,687 band rows, 0 gate-unit
FAILs**, coverage **PASS**): no thermostat schedule introduced; `G8.16` **PASS = 3,520 / 0 FAIL** with the
fold read from the bundle manifest and the diary located by content; `phi_int_mean_w_m2 = 3.0` with a
mean-residue bound of `5e-11`; 8,760 rows with the day boundary declared.

⚪ `Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md` §10 de-staled the same night — its *"only remaining
blocker"* header is superseded in place and kept underneath as the record of what was asked for.
🔴 **MVP §12.11's receiving step is on the OpenUBEM side and is theirs to correct**; 4J cannot and
should not edit it.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified live at filing time and unchanged. No
threshold moved, no checker edited, no number re-derived to make the notice read better. Backups verified
non-empty before every edit (`.bak_wi101`).


### 2026-08-26 (night, last) — 🟢 work item 10.4 is DONE: per-dwelling assignment and emission

`tools/4thJ_step10_assign.py`, `Step10_docs/impl/2026-08-26_work-item-10.4_per-dwelling-assignment.md`.
**297 buildings → 1,576 dwellings → 7,880 emitted hourly CSVs.** `G10.13` **PASS** on 9,365 rows,
`G10.8` **PASS** 0 of 1,576 wrong-fold, `G10.9` **PASS**, `G10.19` **`NOT_EVALUABLE`**, `W10.8`
**PASS**. Battery **6 of 6**. ⚪ **The tool, not a campaign** — no EnergyPlus, and none owed here.

🔴 **`G10.19`'s `NOT_EVALUABLE` is the substantive result of this item.** Qualifying buildings
— Arm D with `N_u ≥ 2` — are **es 9 · uk 5 · it 3** against the **30 per fold** `H10` needs; the whole
census offers **18** Arm D buildings. §6 said the geometry limit was severe; this measures it on the
artefact, **before** a campaign exists rather than after.

🔴 **Not every perturbation expects FAIL, and pretending otherwise would have been the bug.**
`G10.19` never returns FAIL — a vacuity guard that could fail would be a hypothesis test. Its defect
mode is **saying PASS on a manufactured population**, so its case is scored on flipping
`NOT_EVALUABLE → PASS` when the arm is read from `zone_count` and 279 fallback buildings' storeys
become Arm D dwellings.

🔴 **Three defects the battery found in the tool's own first draft, and the MISS is what found
the first one:**

1. **`G10.8` returned PASS on an EMPTY population.** A perturbation pointed every dwelling at a fold
   with no pool; every building was skipped, **zero** dwellings were assigned, and the gate read
   *0 unlocatable, 0 wrong-fold* → **PASS**. **A gate whose population is empty has not been
   satisfied, it has not been asked** — `FINDING 95` / `FINDING 127`. `G10.8` and `G10.13` now return
   `NOT_EVALUABLE` on empty input.
2. **The perturbation was itself badly designed** — it *removed* the gate instead of testing it.
   Replaced by `mislabel_fold`: the diary really is drawn from the right fold and the dwelling
   **records a different one**. It fells `G10.8`.
3. **Globbing `Step7_docs/outputs_step7/schedules/` picked up the wrong bundles** — `leg4_*`, the
   `_cal<year>` survey-calendar variants and seven `perturb_*` bundles. `perturb_hours_8759` has
   8,759 values and **the reader refused it**, which is the reason nothing silently emitted a short
   year. 🔴 **A manifest filter alone is not enough**: `perturb_null`'s manifest is
   indistinguishable from a production one, because the null perturbation *is* "change nothing". The
   bundle set is now read from the **campaign's own `schedule_bundles` field** — the artefact `G8.16`
   traces — with the manifest check as a second opinion.

🔴 **The `G10.13` bound is tight**: largest deviation **1.347e-10 W/m²** against **1.5e-10**,
**90 % of the allowance used**, and the bound is derived from `%.10f` rather than chosen to clear the
result. ⚪ Reduced in flight (2.6 GB per run × six runs): every file is **read from disk at the moment
it is written**, so `V10.h` is intact — **what is dropped is the artefact, never the measurement**.

⚪ Exercised on the **real** OpenUBEM layout census with one declared change, the country label,
because that census is French and France is not a fold. `prereg.md` md5
`e4243e07cdd80c9c846b91f40e3e8c45` verified live by `W10.8`, untouched.

### 2026-08-27 — 🟢 work item 10.9 is DONE: the paired Case A / Case B emission

The pairing exists and is gated. **297 buildings → 3,152 paired rows → 15,760 emitted hourly CSVs →
2,970 cells → 1,485 `delta_div` rows, 0 refused.** `G10.20` **PASS** on all four of its clauses —
0 missing partners, 0 geometry mismatches, 0 cross-building rows, 0 refusals, **15,760 files scanned**
(`V10.d`, a search gate that scans nothing passes everything). `W10.11` **PASS**, 143 of 143 Arm D rows
identical to 10.4's shipped table. Full record in §9.2 and
`impl/2026-08-27_work-item-10.9_paired-case-a-case-b.md`.

🔴 **Three findings, and all three point the same way: the driver channel is degenerate, so nothing
about `H10` can be settled before EnergyPlus runs.** `FINDING 158` — `CF_phi = 1` in 1,450 of 1,450
Case B cells, minimum **396** fully coincident hours per cell. `FINDING 159` — `q99` equals the peak in
2,970 of 2,970 cells. `FINDING 160` — `delta_div` is smaller than the Case-A choice spread in **0 of
290** rows, medians 0.198 / 0.295 of it.

🔴 **And the battery felled one of our own guards.** The first `W10.9` scored `G10.21`(ii) literally and
its designated defect **passed** it. Rewritten to score series identity; the `CF = 1` arm ships stamped
`CARRIED, NOT SCORED`. No threshold moved; `W10.9` was tightened and `W10.12` added.

⚪ **What 10.9 does NOT deliver, stated here rather than left to be discovered:** no EnergyPlus, no
simulated power, no `CF`, no `sqrt(N)` fit, no `H10` verdict. Work item **10.10 now depends on 10.6**
as well as 10.9 — `FINDING 158` removed the route by which it might have started early.
