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

🔴 **2026-08-27 — `EU-04`'s blocker moved, and it moved somewhere Step 10 should read before
planning any cell.** `D-EU-22` was ruled (Option F1) and its coverage probe ran: Madrid's Catastro
INSPIRE `BU` covers, so `S3` becomes an **FR + ES** binational sample; London is **credential-blocked**
behind a GOV.UK One Login token (unmeasured, not zero); Bologna has no per-building construction year
in any ruled open source and is out on typology regardless. ⚪ An independent second measurement
run from this side by a different route (Catastro WFS ad hoc `BBOX`, 48 tiles, rather than the ATOM
bulk download) reproduces all three verdicts: **1883 residential features in the study bbox, 1883
of 1883 carrying a year, and 1183 of 1194 EU-02 footprints (99.1 %) recovering an observed
year AND an observed dwelling count.**

🔴 **But the binding ceiling turned out not to be attributes at all, and this is what reaches
Step 10.** The ruled OpenUBEM layout contract — convex, courtyard-free, at least 8 m wide —
accepts only **204 of 4186** footprints across all four sites (`ES` 63 · `FR` 52 ·
`GB` 49 · `IT` 40), and clearing it is still not emission: in Lyon, the only site where
emission has been measured, **18 of 28** clearers actually emitted (64.3 %). So attributes
would make 1,183 Madrid footprints usable and **geometry accepts 63.** `D-EU-23` is now the arc's
one OPEN decision and **no `S3` sample may be frozen until it is ruled**
(`OpenUBEM/docs/docs_ACTIVE/europeanLocations/debugs/docs/DECISION_REQUEST_D-EU-23_s3_geometry_mode_2026-08-27.md`).

⚪ **Consequence for Step 10, stated so it is not read as worse news than it is.** Step 10's own
population is the **real-stock neighbourhoods**, not `S3`; `10.4` and `10.9` already ran on 297
buildings and 1,576 dwellings. What `D-EU-23` gates is the `S3` ladder rung that `EU-04` must clear
before the arc completes, and `EU-04` completing is what §STATUS above says 10.3 / 10.5 / 10.6 / 10.7 /
10.8 / 10.10 wait on. 🔴 It also puts a number on something Step 10 has never had one for:
**a dwelling-partitioned population large enough for `G10.19`'s 30-per-fold `H10` requirement does not
exist in this corpus** — `G10.19` already said so from the artefact (es 9 · uk 5 · it 3), and the
geometric census is the upstream reason why.

🟢 **Work item `10.1`'s chaining closure notice has been RECEIVED on the OpenUBEM side,
2026-08-27.** It was filed on 2026-08-26 and nothing in the OpenUBEM tree referenced it until now:
MVP §12.11 receiving step 3 still read *"that block is D-EU-09, upstream in Step 7, and it is not
OpenUBEM's to lift"*, and Table 21 still carried `D-EU-09` as the arc's only remaining block. Both now
record the block as **lifted by reference**, and the `EU-06` work-package row with them. ⚪ This
records a lifted block, **not an executed cell**: the 408 `f > 0` runs are still unexecuted and
§9.4 still assigns their execution to GSSCanada. `v1.0`'s frozen `schedule_status` values were
**not** edited, because `v1.0` is immutable.

🟢 **2026-08-27 (later) — `EU-04` moved again, and this time a cell ran.** `D-EU-23` was
**RULED G1** — `S3 = 96` in mixed mode, both axes printed — and it was **executed end to end
the same day**. The Madrid attribute ingestion ran as a **sidecar** (2,084 Catastro features in the
study bbox, 1,183 of 1,194 EU-02 footprints credited a partner, 1,178 carrying a year **and** a
dwelling count, all 28 `eu02` files SHA-256-identical before and after), lifting Spain's
`layout_ready` from **0 to 958**. `S3` was frozen at **96** (FR 69 / ES 27, **12
dwelling-partitioned / 84 massing**) by an input-only rule, and its **annual** campaign completed
**95 of 96** with 0 severe and 0 fatal across those 95, EUI **min 29.5663 / median 80.3233 / max
222.2945 kWh/m²** pooled **66.8677**, in **471.10 s** total.

🔴 **BASIS, added additively 2026-08-27 — those figures are HEATING-ONLY, and the sentence above must
never be quoted without the word.** `eui_kwh_m2` is `heating_kwh / floor_area_m2`, where `heating_kwh`
is the annual sum of the hourly `Zone Ideal Loads Zone Total Heating Energy` `Output:Variable`
(`run_eu_s2_campaign.py::_extract_heating_kwh`). **No lighting, no appliance electricity, no DHW, no
cooling.** A reader who takes the column at its name gets a whole-building EUI wrong by a large factor
in the direction that looks plausible. An off-path meter sidecar over copies of the same 95 IDFs
measured the model's site total at **93.768 kWh/m²**, ratio **1.4023**, with every promoted artefact
unmoved. 🔴 **`93.768` is NOT a whole-building EUI either:** heating + `InteriorEquipment:Electricity`
is **100 %** of it (residual **0.02 kWh over 10.67 GWh**), and an object census of a promoted IDF finds
**`Lights` 0, `ElectricEquipment` 0, `People` 0, `WaterUse*` 0, cooling coils 0**. The `S3` models
contain exactly **two** end uses, so no TABULA or national-EUI comparison is reachable at this rung.
Record: `docs/2026-08-27_OpenUBEM-response-intake_S3-basis-and-population.md` (`FINDING 169`,
`FINDING 171`).

🟢 **All of the above was RE-MEASURED FROM THIS MACHINE on 2026-08-27, not accepted as reported.** The
OpenUBEM tree is at **`C:\Users\o_iseri\Desktop\OpenUBEM`** — a **sibling** of `GSSCanada`, which is why
a `find` bounded to `Desktop\GSSCanada` had previously returned nothing and the nothing was written
down as *"the tree is not on this machine"*. 🔴 **`FINDING 172`: that recorded limit was a scoping
error, and it is this arc's fifth stale-blocker-with-a-written-reason — the first one of ours.** Every
load-bearing figure in the OpenUBEM response re-derives here **exactly**: 95 of 96 with 0 severe /
0 fatal, 95 distinct `idf_sha256` and 2 `weather_sha256`, pooled **66.867688** over **113,768.5830 m²**,
min/median/max **29.5663 / 80.3233 / 222.2945**, sidecar **95/95 identical at `max_abs_diff = 0.0`**,
site total **93.768143**, ratio **1.402294** — and **96 of 96 recorded `idf_sha256` recompute from the
files with 0 mismatches**, which is stronger than the three-hash spot check they reported. ⚪ A negative
search result is only as strong as its root; any future *"X is not available from here"* must print the
root it searched.

🔴 **POPULATION, same intake: the `S3` dwelling population is 26, in 12 buildings.** Verified here by
summing `zone_count` by `layout_mode` over the manifest: **`DWELLING_LAYOUT_EMITTED` 12 buildings /
26 zones**, **`FALLBACK_PENDING_LAYOUT` 83 buildings / 348 zones**, total **374** over the accepted 95
(**381** over all 96 — the extra 7 are the zones of the one fatal building). ⚪ *"374 dwellings"* is
false; 374 is a **zone** count, and 348 of those zones are massing floors. 🔴 **26 is the ceiling on any
per-dwelling statistic taken over the `S3` corpus** — the same shape as `G10.19`, where `H10`'s
dwelling-partitioned population is es 9 · uk 5 · it 3 against a required 30 per fold. Neither reaches 30.

⚪ **And one constraint for whoever first reads an `S3` electricity series:** at `f = 0` **all 381 gain
CSVs are flat at exactly `3`** — 8,760 rows each, one distinct value, 0 non-flat, verified here. The
`OtherEquipment` `1` is a multiplier (`Watts/Area`) and the `Schedule:File` type limits are
`AnyNumber_Wm2`, so the CSV *is* the gain. The non-heating 40 % of `S3` therefore carries **zero
occupancy signal** at `f = 0`, and a null found there would be an artefact of the input, not a result.
No 4J document currently reads it that way — checked by grep, which returned nothing.

🔴 **What that does and does not do for Step 10.** It does **not** produce a Step-10 cell:
the 408 `f > 0` runs are still unexecuted and §9.4 still assigns them to GSSCanada. What it does
is retire the *reason* `EU-04` was open. `S3`'s acceptance is **half met** — the resource
envelope is measured; the exclusion census (469 rows, each with a named reason) and one classified
EnergyPlus failure **await an owner ruling**
(`OpenUBEM/docs/docs_ACTIVE/europeanLocations/ACCEPTANCE_S3_promotion_2026-08-27.md` §6).
⚪ Until those two answers land, `10.3 / 10.5 / 10.6 / 10.7 / 10.8 / 10.10` still wait on
`EU-04`, but they now wait on **an approval**, not on a measurement.

⚪ **One number this step quoted is corrected.** The `18` dwelling-partitioned Lyon buildings
recorded above and in `FINDING`s that cite the layout ceiling is **28 of 297**; the 10 rows once
refused as `PARTITION_AUDIT_FAILED` now emit, because the layout generator rotates about the
footprint centroid and audits against a relative tolerance. The withdrawal is additive in
`layout_contract_ceiling.CORRECTION.json`. 🔴 It does **not** rescue `G10.19`: corpus-wide
only **79 of 1,255** attribute-ready buildings emit a dwelling layout at all, so a
dwelling-partitioned population of 30 per fold still does not exist in this corpus.

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

### 2026-08-27 (response intake) — ALL FOUR `S3` CHALLENGES CAME BACK ACCEPTED, AND THEN THE TREE TURNED OUT TO BE LOCAL, SO ALL OF IT WAS RE-MEASURED

Record: `docs/2026-08-27_OpenUBEM-response-intake_S3-basis-and-population.md`. Incoming:
`../messages_OpenUBEM/2026-08-27_OpenUBEM_to_4J_response_S3_EU-05-06_challenges.md`.

🔴 **`FINDING 172` — the recorded "hard limit" was a scoping error, and it is the arc's FIFTH
stale-blocker-with-a-written-reason, the first one of ours.** `RESUME.md`'s entry of
2026-08-27 (night, last+3) §2 says in bold that the OpenUBEM tree is not on this machine and that no
`S3` / `EU-05` / `EU-06` number *can* be verified from here. The `find` behind it was bounded to
`Desktop\GSSCanada`. **The tree is a sibling, at `C:\Users\o_iseri\Desktop\OpenUBEM`.** An entire arc of
correspondence was conducted as *challenges from reported figures*, under a standing caution that none
of it was checkable, when direct measurement was one directory up. ⚪ The three challenges were still
right — which is exactly why this is recorded: **a correct conclusion reached under a false constraint
is not evidence the constraint was harmless.** The rule *test the reason, do not inherit it* had been
applied outward four times and inward never. **A negative search result is only as strong as its root.**

🟢 **Re-measured from here, read-only, and every load-bearing figure they reported is EXACT.** 96 rows,
`eplus_return_code` 95×`0` / 1×`1`, 0 severe and 0 fatal over the 95; 95 distinct `idf_sha256`,
2 `weather_sha256`; pooled heating-only **66.867688** over **113,768.5830 m²**; min/median/max
**29.5663 / 80.3233 / 222.2945**; sidecar **95 rows, `identical` True ×95, max `max_abs_diff` 0.0**;
site total **93.768143**, ratio **1.402294**; heating + `InteriorEquipment:Electricity` residual
**0.020000 kWh over 10,667,868.78 kWh**; manifest SHA-256 `e90652c6…4de909` as recorded; and **96 of 96
recorded `idf_sha256` recompute with 0 mismatches** — stronger than the three-hash spot check they
reported. Nothing they said was overstated.

🔴 **`FINDING 169` — the unlabelled EUI was live in exactly one 4J place**, § `2026-08-27 (later)` of
this document, corrected **additively**: the original sentence stands and a BASIS paragraph follows it.
The other hits are correspondence, a ruled decision record and two dated `RESUME` entries, none
rewritten; the `Step8_docs/` hits are coincidental digit matches, opened before being dismissed.

🔴 **`FINDING 171` — `93.768 kWh/m²` is not a whole-building EUI either.** An object census of a
promoted IDF finds **no `Lights`, no `ElectricEquipment`, no `People`, no `WaterUse*`, no cooling
coil** — present are 4 `OTHEREQUIPMENT`, 4 `SCHEDULE:FILE`, 4 `HVACTEMPLATE:ZONE:IDEALLOADSAIRSYSTEM`.
The correction owed is not *heating-only → whole-building*; it is that the `S3` models contain **two**
end uses. No TABULA comparison, no national-EUI comparison and no `N1` projection is reachable at this
rung, sidecar or not.

🔴 **`FINDING 170` — their letter addresses the DHW arm as `G11.15`, an ID that moved the same day.**
Since `FINDING 168`, `G11.15` is the double-count gate and the DHW per-dwelling arm is `G11.18`; acting
by ID would have amended the wrong gate. ⚪ On the merits neither of their two asks needs a change:
nothing on the 4J side was ever scoped against 95 or 374, and `G11.18` inherits `G9.15`'s
**200 l/day ±10 %** from the HETUS trigger output, never from `S3` — which contains no DHW term to
calibrate against. **Rule: a cross-tree message naming a gate must name its date.**

⚪ **Nothing in this intake moved a 4J gate, band, threshold, verdict or count; no 4J code ran; nothing
in the OpenUBEM tree was written.** Step 11 is still blocked on the **408 unexecuted `f > 0` runs**
(§9.4, GSSCanada) — compute, not a decision.

### 2026-08-27 (later) — 🔴 `FINDING 173`: THE 408 `f > 0` RUNS CANNOT BE SUBMITTED, AND THE REASON IS NOT THE CHAINING RULE. **THERE IS NO EXECUTOR.**

Written after an attempt to prepare the `sbatch` for them. **The sbatch was not written, because
there is nothing for it to invoke.** Measured from both trees on this machine, read-only.

🔴 **1. Nothing consumes the frozen cell specification.** `grep` for
`eu_campaign_cell_spec_v1.0.json` and for `cell_spec` across every `.py` and `.sh` in
`C:\Users\o_iseri\Desktop\OpenUBEM\scripts\` and `\openubem\` returns **exactly one hit**:
`scripts/freeze_eu_campaign_cell_spec.py:53`, the script that **wrote** the file. No reader. The
same grep across `4J_docs_occ/tools/` returns **none**. §9.4 is signed `CLOSED` and the spec is
`FROZEN_PINNED` at **510 cells / 510 unique `cell_id` / 0 unpinned weather** — all of which is
true, and none of which is an executor. ⚪ **A closed contract is not a built runner**; §9.4 closed
the *specification*, and `EU-08` — *"Execution of the 510 cells"*, owner **GSSCanada** — is a
separate row of §9.7 and is still `In progress`.

🔴 **2. The artefacts the spec points at do not exist.** Every cell names
`idfs/<cell_id>.idf`, `schedules/<cell_id>.csv` and `manifests/<cell_id>.json` relative to a
campaign root. `find` for directories named `idfs` or `manifests` under the OpenUBEM tree returns
only unrelated US fleet and pytest-temp trees; **no campaign root exists**. There are no IDFs, no
gain CSVs and no cell manifests for any of the 510.

🔴 **3. The 102 `f = 0` control cells are ALSO unexecuted.** Their `schedule_status` is
`READY_F0_CONTROL`, which says the *schedule* is ready, not that the *cell* has run. ⚪ **The
blocker was never "408 of 510"; it is 510 of 510.** Any plan that treats the controls as done and
the `f > 0` cells as the remainder is wrong by 102 runs.
🔴 **Do not confuse this campaign with the `S3` campaign.** `S3` is 96 real-footprint buildings
(FR + ES), it has run, and its 381 flat gain CSVs are a different artefact set entirely. The 510
are **102 TABULA archetypes × 5 `f`** over `es`/`uk`/`it`. Two campaigns, two populations; the
`f = 0` figures of one say nothing about the other.

🔴 **4. The spec's own frozen field still reads `BLOCKED_CHAINING_RULE` on all 408.** `v1.0` is
immutable and work item `10.1` lifted the block **by reference**, in a document — not in the JSON.
⚪ A runner written to trust the spec's `schedule_status` would therefore **refuse all 408 by
construction**, and would be right to, since the field is what it was frozen as. Whoever writes
the executor must read the lift from `Step10_docs/docs/2026-08-26_10.1_chaining-closure-notice.md`
and record that it did so. **This does not justify editing `v1.0`; a change produces a `v1.1`.**

🟢 **What DOES exist, so the gap is bounded and is a driver, not a capability.**
`openubem/semantic/european_schedules.py::emit_step8_gain_schedule` /
`build_step8_gain_series` implement the `f > 0` gain law
`phi(t) = 3.0 · ((1 − f) + f · g(t)/mean(g))` and accept every `f` in the frozen set; the 102
TABULA archetype records exist; all four weather folds are `RULED_PINNED_EXCEPTION` with a hashed
EPW verified on disk; and **EnergyPlus 24.2.0 is installed on Speed** at
`~/ep_install/EnergyPlus-24.2.0-e7ecb2d53b-Linux-Ubuntu22.04-x86_64`. The missing piece is the
driver that walks the spec, emits each gain CSV from a 4J presence series, builds the IDF, runs
E+, and writes the cell manifest of §9.6.

🔴 **The ownership question this raises, and it is the author's, not mine.** §9.4 gives OpenUBEM
*"dwelling/core geometry and watertight IDF generation"* and *"EnergyPlus execution, parsing, and
low-level meter integrity"*, while §9.7 gives GSSCanada *"Execution of the 510 cells"*. **Those two
rows are consistent only if OpenUBEM supplies the per-cell build-and-run entry point and GSSCanada
drives it.** No such entry point is exported today. ⚪ Filed as a question, not a decision:
whichever tree writes it, it must not be written twice.

⚪ **What this entry changes: nothing.** No gate, band, threshold, verdict or count moved; no code
was written or run; nothing in the OpenUBEM tree was written. Step 11's blocker is **re-stated,
not lifted** — and it is now stated correctly: **510 unexecuted cells and no executor**, where the
record previously said *408 runs, compute not a decision*. 🔴 **"Compute, not a decision" was
wrong.** It is not compute; there is nothing to compute with yet.

### 2026-08-27 (night) — AMENDMENT TO `FINDING 173`: AN EXECUTOR *DOES* EXIST, FOR ANOTHER POPULATION — AND THE ASK TO OPENUBEM IS NOW ONE FUNCTION, NOT A CAMPAIGN

🔴 **`FINDING 173` point (1) says *"There is no reader and no executor anywhere."* The first half stands
and is unchanged. The second half is too strong and is corrected here, additively, before it is
quoted.** The entry above is not rewritten; this paragraph is what a later reader must carry with it.

🟢 **An executor exists — for a different population.** `OpenUBEM/scripts/run_eu_s2_campaign.py` and
`scripts/run_eu_s3_campaign.py` build IDFs, invoke EnergyPlus, parse the heating series and write a
campaign manifest; `S3` imports `build_geometry_for_row`, `build_idf_for_building` and
`run_energyplus_for_building` from `S2`, and **`S2` already calls `emit_step8_gain_schedule`** per
dwelling zone (line 267), with the fixed-name `SCHEDULETYPELIMITS` duplication handled at line 263.
That path has been exercised on the **96 real-footprint `S3` buildings**, 95 accepted.

🔴 **What it is not, measured field by field rather than asserted.** (a) Its population is a frozen
`S3` sample of **real footprints**, not the 510 rows of the spec. (b) Its geometry comes from a **GPKG
footprint manifest** — and the 510 cells carry **no footprint reference at all**, a cell being
`archetype_id × weather_id × f` and nothing else. (c) `f` is a **module constant `SENSITIVITY_F = 0.0`**;
`presence` and `chaining_rule` are **never passed**. (d) It writes a **flat campaign CSV**, not the
§9.6 per-cell JSON manifest.

⚪ **So the corrected statement of the blockage is:** the missing pieces are a **driver** (walk the
spec, supply `g(t)`, order the runs, submit the array) and an **archetype-only geometry route**
(TABULA record → conditioned plate → zones, with no OSM polygon). `derive_european_plate_area` is
documented as valid *"for synthetic-average rows as well as for integral source rows"*, so the
ingredients exist; the plate-to-zones step for a building with no measured outline does not.

🟢 **The ownership question of `FINDING 173` §7 is now answered as a recommendation and sent.**
`Step 9.4` gives OpenUBEM *"dwelling/core geometry and watertight IDF generation"* and *"EnergyPlus
execution, parsing, and low-level meter integrity"*, and gives GSSCanada *"the five-level campaign
matrix and run ordering"* and *"Step 8 `manifest.json`, gate scoring"*; §9.7 assigns `EU-08` —
*execution of the 510 cells* — to GSSCanada. 🔴 **Those rows are consistent under exactly one reading:
`EU-08` is the LOOP, not the ENGINE.** OpenUBEM exports one per-cell entry point
(`run_campaign_cell(cell, *, archetype_record, presence, chaining_rule, run_root, dry_run)` returning
the §9.6 manifest); GSSCanada writes the driver around it. Two reasons this is the right side of the
line: the §9.6 manifest demands `openubem_git_commit`, `energyplus_version` and
`energyplus_build_hash` — facts only their tree observes — and §9.4 explicitly forbids GSSCanada from
reaching into OpenUBEM geometry or IDF internals, which is what a GSSCanada-side IDF builder would do.

⚪ **Sent 2026-08-27** as `messages_OpenUBEM/2026-08-27_4J_to_OpenUBEM_EU-08_executor_entry_point.md`
(102 lines), copied into their inbox at
`OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/`. It also withdraws, to them, the
*"408 runs — compute, not a decision"* sentence of the previous letter's §6.

🔴 **Two constraints the driver must satisfy, recorded here because no gate would catch either.**
(1) It must read the `f > 0` lift from `Step10_docs/docs/2026-08-26_10.1_chaining-closure-notice.md`,
**not** from the frozen `schedule_status`, and **record in each cell manifest that it did so**, with
the notice's identity rather than a boolean — a runner that silently ignores a frozen `BLOCKED_*`
field is indistinguishable from one that never read it. (2) `eu_campaign_cell_spec_v1.0.json` must
never be amended; restating the statuses inside the file produces a **`v1.1`**, and `v1.0`'s digest
must survive it.

⚪ **One question raised to them, not decided here: 102 versus 88.** The spec is 102 archetypes × 5 =
**510**; the 4J side's own Step 8 injected campaign is 88 archetype cells × 5 = **440**, because the
`4a`/`4b` rulings turn TABULA rows into cells (es 24, uk 32, it 32). **They are two different
campaigns and nothing here reconciles them** — but the archetype populations differ by 14, and any
figure carried between them must cross that difference deliberately.

⚪ **What this amendment changes: nothing scored.** No gate, band, threshold, verdict or count moved;
no code was written or run; nothing in the OpenUBEM tree was written but the message named above.
Step 11 remains blocked, **510 of 510**, and what is owed is now **one exported function and one
geometry route on their side, and the driver on ours** — not compute.

---

#### 🟢 **2026-08-27 (night, last+10) — `D-S10-7` / `D-S10-8` / `D-S10-9` ARE RULED AND DELIVERED; AND THREE INTAKE FACTS IN §1 OF THIS DOCUMENT ARE STALE (`FINDING 177`).**

🔴 **1. `FINDING 177` — THREE FIGURES IN THIS DOCUMENT'S OWN OPENING SECTION ARE SUPERSEDED, AND ONE OF THEM IS WITHDRAWN AT SOURCE.** They are corrected here **additively**; the original paragraphs above are left as written, because they were true on the day they were taken.

* 🔴 **The `18 of 28` / `64.3 %` survival figure (line ~33) is WITHDRAWN**, not updated. Source: `OpenUBEM/openubem/outputs/eu_evidence/EU-04/D-EU-22/layout_contract_ceiling.CORRECTION.json`, which marks it `status: WITHDRAWN` in its own words. The `18` came from the `S1` layout-reachability census written 2026-08-25 14:28, which **predates the partition-audit fix committed the same day at 16:04** (`5e739b5` — rotation about the footprint centroid, `openubem/geometry/european_residential.py:511`, plus a footprint-area-relative topology tolerance at `:687`). Re-measured on the identical 297 Lyon footprints, same native `EPSG:32631`, unmodified contract code: **all 10 rows that had failed `PARTITION_AUDIT` now emit.** Lyon is **28 of 297**, and **28 of its 28 geometric clearers emit (1.00)**. 🔴 **The 64.3 % survival calibration may never be quoted again**, here or anywhere.
* 🔴 **`D-EU-23` is not "the arc's one OPEN decision" — it was RULED the same day, Option G1**: `S3 = 96` in **mixed mode**, dwelling-partitioned where the `EU-04` contract emits and the already-ruled `one_zone_per_floor` fallback elsewhere, with the layout axis and the simulation axis printed in **separate columns in every `S3` acceptance panel**. ⚪ **The ruling is unaffected by the correction above**: 79 < 96, so mixed mode is still required and the no-quote-without-split caveat still binds — only the number inside it moved.
* 🔴 **London is no longer "credential-blocked (unmeasured, not zero)" — it is MEASURED, and it is OUT.** A live MHCLG EPC probe under an owner-supplied bearer token (11,114 calls, 4,431.6 s, zero 429) found **797 of 1,219** strict-join footprints carrying an observed construction-age **BAND** = **65.38 %**. 🔴 **`GB` stays out of `S3`** on four grounds, of which the first is the one that matters to us: the quantity is an RdSAP age **band, not a year**, and converting it is **ASSIGNMENT** — the exact ground that ruled Italy out. ⚪ **`65.38 %` must never be printed beside the `ES` `98.74 %`**: one is certificate coverage over a sold/let/new-since-2008 population, the other is a stock census.

🟢 **The corpus-wide measured figures that replace the projections: `79 of 1,255` emit (`ES` 51 + `FR` 28), and `12 of 96` inside the frozen sample.** ⚪ `~40` and `~73` were planning projections and are **replaced by measurement**; they may never be quoted again either.

⚪ **2. WHY THIS WAS FOUND AT ALL.** It was not audited for. The `2026-08-27` reply-check walked their tree for an `EU-08` answer, and their `MVP` and progress log had moved. **Same class as `V10.i` and `FINDING 176`: a recorded fact carries the date it was last measured, and three of ours had aged out inside 24 hours.**

---

🟢 **3. THE THREE DECISIONS ARE RULED.** Full record: `IMP/docs/2026-08-27_D-S10-7_D-S10-8_D-S10-9_the-presence-series-binding-and-the-uk-calendar.md` §9. They arose from `messages_OpenUBEM/2026-08-27_OpenUBEM_to_4J_EU-06_f-gt-0_presence_binding_request.md`, in which OpenUBEM **accepts** the `EU-08` loop-not-engine reading (the `run_campaign_cell` entry point is queued on their side) and **accepts all four** `10.1` chaining-closure artefacts. 🔴 **The chaining rule is therefore no longer the blocker on the 408.**

* **`D-S10-7` — 🟢 Option (b). `uk` stays at 2014.** The diary year and the calendar year are ruled to be **the same physical quantity**. 🔴 So OpenUBEM's `A2` ask — emit a `uk` `_cal2015` bundle to match a pinned `y2015` EPW — was **not** taken: it would have reversed `D-S10-1` item 2 by running a script. Instead we ask them to **repin `uk` to `uk_london_2014_2015_y2014.epw` in a `v1.1`** (sha256 `7b7d9524d6667d79572a3453b7ece531a6b2717dd496aaa239ec925fbce6e295`), a file **already on disk in their tree** — so the repin costs no data. `v1.0` is retained and never amended. ⚪ Result: all three axes agree for the first time — `es` 2010 · `uk` 2014 · `it` 2014, ruled year = EPW calendar = bundle calendar.
* **`D-S10-8` — 🟢 deterministic rank-order binding.** Archetype at rank `i` (by `archetype_id` within fold) is driven by the household at rank `i` (by sorted `hid`); **one dwelling per cell**; **all five `f` levels share one series**. 🔴 **Per fold the counts are `es` 24 · `uk` 36 · `it` 42, all below the 100 shipped series, so the map is strictly bijective and nothing wraps.** ⚪ Our own earlier framing — *"102 archetypes against 100 series"* — was a corpus-level comparison that **overstated the problem**, and is corrected here and in the letter.
* **`D-S10-9` — 🟢 `leg5_it_independent_seed1_cal2014` emitted additively**; `cal2013` left byte-identical and re-verified after the write.

🟢 **4. WHAT IS ON DISK NOW.** `Step10_docs/outputs_step10/eu_cell_presence_binding_v1.json` — **510 of 510 cells bound**, each row carrying `rank`, `archetype_id`, `hid`, `presence_csv` and the series `sha256`. Emitter `tools/4thJ_step10_presence_binding.py`. Three §9.5 addenda at `leg5_{es_cal2010,uk_cal2014,it_cal2014}/manifest_addendum_9_5.json` from `tools/4thJ_step10_presence_addendum.py` — **no bundle re-emitted, no series hash moved.**

🔴 **5. THE `it` EMISSION WAS PROVEN BEFORE IT RAN, BECAUSE THE ORIGINAL INVOCATION WAS NEVER RECORDED.** `provenance` is `null` in every Step 7 manifest and no document carries the command line. So the reconstructed invocation was first used to **re-emit `cal2013` into scratch**: **100 of 100 CSVs byte-identical**, `manifest.json` identical, back-off depths reproduced (`{3: 6510, 4: 70870}`, share 0.9159). **Only then was `--year 2014` changed.** ⚪ Read back from the new artefact: `year 2014`, `seed 1`, `n_households 100`, 8,760 expected and every series at 8,760 data rows + 1 header, `rotated_to_midnight true`, `diary_origin_hour 4`, 102 files.

🟢 **6. THE BINDING TOOL'S GUARDS WERE SEEN FAILING, NOT ASSUMED.** Three falsifiers were run and **all three refused with the intended message and wrote no partial artefact**: (i) the stale `it` `cal2013` bundle → refused on calendar; (ii) the `year 2017` `uk` bundle → refused on calendar; (iii) a fold mismatch → refused. 🔴 The tool also **refuses rather than wraps** if a fold ever exceeds the shipped series count — a silent modulo would give two archetypes the same occupant and **no downstream gate could see it**.

🔴 **7. TWO THINGS THAT MUST TRAVEL WITH THE BINDING.** **(i)** It carries **no occupant semantics** — a spec cell holds no occupant attribute, so this is an **arbitrary but fixed** pairing and **may never be called representative or stratum-matched**; the artefact carries that warning inline so it cannot be separated from the data. **(ii)** The driver must take the series **from the artefact**, never by re-deriving the order at run time: two sort implementations that agree today are a latent divergence, and the hashes exist so a run can prove which series it read.

⚪ **8. WHAT MOVED AND WHAT DID NOT.** New: two tools, one binding artefact, three addenda, one `it` bundle (102 files), one letter (`messages_OpenUBEM/2026-08-27_4J_to_OpenUBEM_presence_binding_ruled_and_delivered.md`, 240 lines, copied to their inbox), one decision record. 🔴 **No gate was scored; no band, threshold, verdict or count moved; no promoted artefact was edited; no job was submitted and the Speed queue is EMPTY.** `eu_campaign_cell_spec_v1.0.json` was opened **read-only** and is untouched at md5 `15d3b7933803d8c8a5e1de78b0e28d67`. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.

🔴 **What is owed to a person.** **Nothing on this arc.** ⚪ Owed by **OpenUBEM**: the `v1.1` `uk` repin, and the `run_campaign_cell` entry point they have queued. ⚪ Owed by **us the day that function exists**: the driver, the run ordering, the `sbatch` array, `EU-09`/`EU-10` scoring. ⚪ Still open elsewhere and unchanged: `D-S6-16` (a′) or (c′), the `D-S8-3` follow-on, the `D-S8-4` follow-on.

---

#### 🟢 **2026-08-27 (night, last+11) — OPENUBEM ISSUED `v1.1`; THE BINDING IS RE-EMITTED AS `v2` ADDITIVELY, AND THE 408 NOW HAVE A SPEC, A CALENDAR AND A SERIES THAT ALL AGREE.**

🟢 **1. `v1.1` LANDED AND WAS RE-DERIVED HERE, NOT TAKEN ON THEIR WORD.** `openubem/data/campaign/eu_campaign_cell_spec_v1.1.json`, sha256 `16d3fbd62a9f79265c08c5746bbc70f5130cd30cb673c1a68c74755c79aa65f6`, `FROZEN_PINNED`, 510 cells. Recomputed on this side: the `uk` EPW hash `7b7d9524…` **matches**, `v1.0` is **unamended** at md5 `15d3b793…`, the `cell_id` set is **identical**, and a cell-by-cell diff over all 510 gives the **complete** differing set `epw_path` ×180 + `weather_sha256` ×180, **every one of them `survey_fold == uk`** — nothing else on any fold. 🟢 **`D-S10-7` (b) is discharged on both sides.**

🟢 **2. THEIR ACCEPTANCE TEST PASSED, AND IT WAS A REAL ONE.** They reconstructed the `D-S10-8` mapping **from the filed rule text and the bundle directories alone**, reading our `binding` arrays only to compare: **102/102 mappings, 0 mismatches; 102/102 `presence_sha256` match the shipped CSVs; 0 series off 8,760.** ⚪ `sort_order_declared` is what made that possible — a second machine could sort the same way because the artefact says which way that is.

🔴 **3. THEIR ONE NOTE BACK WAS REAL AND IS CLOSED ADDITIVELY.** `eu_cell_presence_binding_v1.json` pins `spec.sha256` to **`v1.0`**, which `v1.1` supersedes — substantively invariant (the binding keys on `survey_fold` and `archetype_id`, neither of which a weather-only revision touches) but **a runner validating that digest against the spec it executes would fail**. 🔴 **`v1` was NOT edited**: they had already verified against it, and editing in place would retroactively invalidate a filed verification. So the same move the spec made: **`Step10_docs/outputs_step10/eu_cell_presence_binding_v2.json`**, re-emitted against `v1.1` with a `supersedes` block, `v1` **retained byte-identical**.

🟢 **4. THE `v1` → `v2` EQUIVALENCE WAS PROVED AFTER THE WRITE, NOT ASSERTED.** Keys new in `v2`: `binding_invariance`, `supersedes`. Keys differing: **`spec`, and nothing else.** **102 binding rows compared, 0 mismatches** — every mapping row and every `presence_sha256` identical. ⚪ So their 102/102 reconstruction transfers to `v2` unchanged and does not need re-running. 🔴 The driver takes its series from **`v2`** now, still never from an order re-derived at run time.

⚪ **5. THE TOOL GAINED ONE ARGUMENT, `--supersedes`,** so the supersession is emitted by the tool and reproducible, not hand-patched into the JSON afterwards. `binding_invariance` is emitted unconditionally and states in the artefact itself why the digest can move while the mapping cannot.

🔴 **6. ONE FLAG SENT BACK, THEIRS TO CLOSE: `v1.1` STILL NAMES `y2015` IN ITS OWN PROSE.** Line 117 carries an `amendment` block inherited from `v1.0` still listing `uk_london_2014_2015_y2015` among the pinned files. **Every machine-readable field is correct**; this is prose only — and it is exactly the `FINDING 177` class, a fact that aged out *inside its own document* where nothing checks it. ⚪ We are read-only on their tree and touched nothing; we noted that amending `v1.1` in place would break the `16d3fbd6…` digest both sides have now filed, so it is a `v1.2` or an addendum, never an edit.

⚪ **7. PROTOCOL, NOW EXPLICIT ON BOTH SIDES.** A direct session channel exists; **the letters in `messages_OpenUBEM/` remain the record of authority and the channel is delivery only.** Each side is **read-only on the other's tree** — a change under `openubem/` is *asked for* and *issued by them*, exactly as `v1.1` was. 🔴 **Decisions go to owners**: neither session rules for the other, and `D-S10-7`/`8`/`9` were each put to our author in writing before anything ran.

⚪ **8. WHAT MOVED.** New: `eu_cell_presence_binding_v2.json`, one letter (`messages_OpenUBEM/2026-08-27_4J_to_OpenUBEM_binding_v2_repinned_and_v1-1_verified.md`, copied to their inbox), their letter filed here. Modified: `tools/4thJ_step10_presence_binding.py` (`--supersedes` + `binding_invariance`), this file (backup `.bak_v2bind`, `[ -s ]`-verified). 🔴 **No gate scored; no band, threshold, verdict or count moved; nothing under `openubem/` written; no job submitted and the Speed queue is EMPTY.**

🔴 **What is owed to a person.** **Nothing on this arc.** ⚪ Owed by **OpenUBEM**: `run_campaign_cell`, the single remaining item. ⚪ Owed by **us the day it exists**: the driver, the run ordering, the `sbatch` array, `EU-09`/`EU-10` scoring. ⚪ Still open elsewhere and unchanged: `D-S6-16` (a′) or (c′), the `D-S8-3` follow-on, the `D-S8-4` follow-on.

---

#### 🟢 **2026-08-27 (night, last+12) — THE `y2015` PROSE FLAG IS CLOSED BY OPENUBEM WITHOUT TOUCHING `v1.1`, AND OUR `v2` WAS VERIFIED ON THEIR MACHINE. NOTHING IS OWED ON THIS ARC IN EITHER DIRECTION.**

🟢 **1. THEIR CLOSURE, RE-DERIVED HERE AND NOT TAKEN ON THEIR WORD.** `openubem/data/campaign/eu_campaign_cell_spec_v1.1_addendum_prose_corrections.json`, sha256 `882ccf62e6e62e844931b0a5e3f3a8a39e5c1386a5f44356417f586527b07692`, `openubem_git_commit 4bd4cad`. One correction, `C-19-PROSE-1`, carrying `incorrect_text`, `correct_text` and a `must_not_conclude` line — *"That any uk cell in v1.1 is pinned to a 2015 EPW."* 🔴 **`spec_amended_in_place: false`, and it holds:** `v1.1` re-hashed here **after** their write still reads `16d3fbd62a9f79265c08c5746bbc70f5130cd30cb673c1a68c74755c79aa65f6`, so **the digest our `v2` `spec` block pins is undisturbed and no `v1.2` exists**.

⚪ **2. THE REMAINING `y2015` STRINGS IN `v1.1` ARE CORRECT.** Three occurrences: line 117 (the `C-19` `amendment`, the one that was wrong and is now corrected by addendum) and `revision_note.change` / `revision_note.previous_uk_epw_path`, which **name the superseded pin deliberately** and are explicitly excluded from the correction. 🔴 A future reader must read `v1.1` **together with its addendum**; the spec itself still contains the stale sentence, because it may not be edited. 🔴 **OpenUBEM records this as a LIVE LIMITATION, not as closed** (acknowledged 2026-08-27): the defect is **relocated, not removed** — `v1.1` carries **no in-file pointer** to the addendum, so a reader who opens the spec alone and reads `C-19` still gets the wrong EPW. They will not touch `v1.1` to fix prose, and an `addendum_refs` array is folded in only if a `v1.2` is ever issued for a **substantive** reason. ⚪ Their own write-backs (MVP §9.7.3, director prompt, walkthrough log) are **their owner’s call and still pending** — until then the pairing lives only in the letter, the addendum and this document.

🟢 **3. OUR `v2` WAS VERIFIED ON THEIR MACHINE.** sha256 `8f94165dab807c5a…`; `v1` retained byte-identical at `333ed4df3bdb7a7e…`; `spec` now `eu_campaign_cell_spec_v1.1.json` / `16d3fbd6…`; `n_cells_bound_total` 510; keys new = `binding_invariance`, `supersedes`, keys differing = `spec` only, keys removed = none; **102 rows compared row-by-row, 0 mismatches, every `presence_sha256` identical**. ⚪ So their `102/102` reconstruction is **not** re-run, and their §4 note is closed on both sides. ⚪ They record that they are copying `binding_invariance` as a pattern — stating **in-artefact** why a digest can move while a mapping cannot.

🟢 **4. THE `run_campaign_cell` MANIFEST SHAPE IS NOW A CONSTRAINT, NOT A PREFERENCE.** They accept it as binding on the callee: the per-cell manifest will record the **cell identity**, the **presence-series path and its `sha256`**, and the **`f > 0` lift by the `10.1` notice's identity** — the same property our three driver constraints carry, that a completed run can prove what it read. ⚪ **The signature comes to us before the driver is written against it.**

⚪ **5. WHAT MOVED.** New: their letter filed at `messages_OpenUBEM/2026-08-27_OpenUBEM_to_4J_c19_prose_closed_and_binding_v2_verified.md`. Modified: this file and `Prompts/RESUME.md` (backups `.bak_c19`, both `[ -s ]`-verified). 🔴 **No artefact re-emitted, no gate scored, nothing under `openubem/` written, no job submitted, Speed queue EMPTY.**

🔴 **What is owed to a person.** **Nothing on this arc, in either direction.** ⚪ Owed by **OpenUBEM**: `run_campaign_cell`, still the single remaining item. ⚪ Owed by **us the day it exists**: the driver, the run ordering, the `sbatch` array, `EU-09`/`EU-10` scoring. ⚪ Still the author's, unchanged: `D-S6-16` (a′) or (c′), the `D-S8-3` follow-on, the `D-S8-4` follow-on. ⚠ **The board is still not re-published.**

---

#### 🟢 **2026-08-27 (night, last+13) — `run_campaign_cell` EXISTS. THE SIGNATURE IS FIXED, RE-DERIVED HERE, AND INTEGRATION-CHECKED FIELD-BY-FIELD AGAINST OUR REAL `v2` AND OUR REAL CSVs. THE 408 ARE NOW BLOCKED ON NOBODY — THE DRIVER IS OURS TO WRITE.**

🟢 **1. THE ENTRY POINT LANDED AND WAS NOT TAKEN ON THEIR WORD.** `openubem/campaign/eu_cell_runner.py`, sha256 `a2deddc911df5c0f9a76e308f4548d0824bd5aba020236b7f533a55ab652f558`, `def run_campaign_cell` at **line 380**. Their "19 tests pass" was re-run on this side, read-only: `PYTHONDONTWRITEBYTECODE=1 py -m pytest tests/test_eu_cell_runner.py -q -p no:cacheprovider` → **19 passed in 2.61 s**, nothing written under `openubem/`. `dry_run` only; no EnergyPlus has been run and no cell simulated on either side.

⚪ **2. THE SIGNATURE, FIXED.** `run_campaign_cell(cell, *, spec_path, spec_sha256, binding_path, chaining_notice_path, schedules_root, run_root, dry_run=False, energyplus_timeout=900) -> dict`. `cell` is one element of the spec's `cells[]` **passed verbatim** and verified field-for-field against `spec_path`; a mutated cell is a **refusal**, not a warning. 🔴 **Iteration, ordering and concurrency are OURS** — the callee runs exactly one cell and every input that determines its result is an explicit argument, so a completed run is reproducible **from its own manifest alone**.

🟢 **3. THE INTEGRATION WAS CHECKED AGAINST THE REAL ARTEFACTS, NOT AGAINST THE PROSE — AND IT COMPOSES.** Every key their runner reads exists in `eu_cell_presence_binding_v2.json`: top level `semantics_warning`, `ruling`, `binding_invariance`, `folds`; `folds[f]` carries `bundle`, `bundle_rule`, `bundle_year`, `diary_origin_hour`, `rotated_to_midnight`, `binding`; each row carries `archetype_id`, `hid`, `presence_csv`, `presence_sha256`, `rank`. On rank-0 of each fold I resolved `schedules_root/bundle/presence_csv` on disk: **file exists, `presence_sha256` matches, 8,760 data rows, header equal to `HH_<fold>_<hid>_Presence`** on `es`/`uk`/`it`. 🔴 **That header check passes only because our `hid` ships as a ZERO-PADDED STRING** (`00035`, `11020212`, `000072`; widths 5/8/6) — had it been emitted as an int, their equality test would have refused **every** cell. It is a real check that happens to pass, not a formality, and any future re-emission of the binding must keep `hid` a padded string.

🔴 **4. TWO ASKS SENT BACK, BOTH ADDITIVE, NEITHER A RENAME AND NEITHER BLOCKING.** **(i) The `f>0` lift authority is a word match, and the word is ordinary English.** `resolve_lift_authority` accepts the notice if `\b<chaining_rule>\b` occurs anywhere in it; our `bundle_rule` is literally **`independent`**, which the notice does contain (lines 40/53/62/87/232/263/270) but so would any document using the word. Asked for an optional `chaining_notice_sha256` argument, refusing on mismatch; the notice is `058c9d132d49db5fca15f2fa3b8d0a161cc947d27559b36fde6233b4a89d74c6` and our driver will always pass it. **(ii) Their refusal #1 is downgradeable through the binding path.** `binding_spec_digest_accepted_by` falls back to `binding_invariance_clause` on the **mere presence** of that key — and `v2` carries it — so a run against a spec digest neither side has ever seen would proceed **with a label instead of a refusal**. It is a presence check where a coverage check is needed. ⚪ Offered: if they require membership, we emit a **`v3`** binding whose `binding_invariance` gains an `applies_to` digest list (`16d3fbd6…` today), `v2` retained byte-identical — the same additive move as `v1`→`v2`. 🔴 **Not done unilaterally: they have filed `v2`'s digest.**

🟢 **4b. BOTH ASKS WERE IMPLEMENTED WITHIN THE HOUR, AND BOTH WERE RE-VERIFIED HERE. NO `v3` IS NEEDED.** Runner now sha256 `1f5f6e6bc2483a886f9a016e664dab92bdd67381bf1bf623bc14f26893a3848f`; **26 tests passed** (`PYTHONDONTWRITEBYTECODE=1 py -m pytest tests/test_eu_cell_runner.py -q -p no:cacheprovider`, run read-only). 🔴 **THE SIGNATURE CHANGED — write the driver against THIS one:** `chaining_notice_sha256=None` is inserted, keyword-only, after `schedules_root`. **(i)** `resolve_lift_authority` checks the declared digest **first** and refuses on mismatch, and the word check is **retained as the second condition** — read at lines 162–197, a correctly-hashed notice that does not name the rule is still refused, which is the right shape: a digest check that silently replaced the word check would have been a regression dressed as a fix. `lift_authority` gains `notice_sha256_declared` beside `notice_sha256`, so a manifest shows whether the caller **pinned** the notice or merely accepted what was on disk. 🔴 **Our driver always passes `058c9d132d49db5fca15f2fa3b8d0a161cc947d27559b36fde6233b4a89d74c6`.** **(ii)** The invariance fallback is now a **membership** test, not a presence test: `binding_invariance` must be an object whose `applies_to` names the digest actually being executed, and a bare truthy clause or an omitting list is a **refusal**. ⚪ **`v2` therefore never reaches the clause** — it pins `v1.1` exactly and resolves by `exact_match` — so the stricter rule is proven not to have changed the run in hand, and **the `applies_to` list is owed only if the spec is ever revised again**, emitted additively on that day. ⚪ The value label became `binding_invariance_clause_covering_this_digest`; it is a rename inside **their** manifest vocabulary and touches **nothing in our artefacts**.

🟢 **5. WHAT THEY BUILT THAT WE DID NOT ASK FOR, AND IT IS RIGHT.** A **bundle-year vs EPW-year mismatch is a refusal** — the `D-S10-7` class exactly: 8,760 rows are produced either way and **no length check can see a day-type misalignment**, so it is gated rather than trusted; a test asserts agreement on `es` 2010/2010, `uk` 2014/2014, `it` 2014/2014. ⚪ Also accepted as written: `heating_source` is the hourly `Zone Ideal Loads Zone Total Heating Energy` **variable, never a meter** — no saved EU IDF carries `Output:Meter` and none is added, because adding one would move **every promoted `idf_sha256`**; `cell['schedule_status']` is **never consulted for gating**, with `schedule_status_frozen_value` + `schedule_status_ignored: true` + the reason recorded, so the frozen `BLOCKED_CHAINING_RULE` stays **visible without being obeyed**; and `occupant_semantics_warning` is copied **verbatim** into every manifest, so the arbitrary-but-fixed nature of the pairing cannot be lost downstream.

⚪ **6. WHAT MOVED.** Modified: this file and the other state doc (backups `.bak_runner`, both `[ -s ]`-verified). 🔴 **No artefact emitted or re-emitted, no gate scored, no band/threshold/verdict/count moved, nothing under `openubem/` written, no job submitted, Speed queue EMPTY.** ⚠ **The board is still NOT re-published** and carries no card for `D-S10-7/8/9`, `FINDING 177`, the `v1.1`/`v2`/addendum arc or the runner.

🔴 **What is owed to a person.** **Nothing on this arc, in either direction.** 🆕 ⚪ **Owed by us, and it is now the only build task anywhere:** the `EU-08` driver over the 510 cells against the signature above — per-fold run ordering, the `sbatch` array (`-t 7-00:00:00`, fire-and-forget), presence wiring read **from `eu_cell_presence_binding_v2.json`** and never from a re-derived sort order, then `EU-09`/`EU-10` scoring. ⚪ Owed by **OpenUBEM**: **nothing** — both §4 asks are implemented and re-verified (§4b); only their own write-backs (MVP §9.7.3, director prompt, walkthrough log) remain, and those are their owner's call. ⚪ Still the author's, unchanged: **`D-S6-16` (a′) or (c′)**, the **`D-S8-3` follow-on**, the **`D-S8-4` follow-on**. ⚪ Optional: **Fuentes et al. (2018)**.

---

#### ⚪ **2026-08-27 (night, last+14) — `GEO-08` WAS RE-BASED ON THEIR SIDE. IT DOES **NOT** ESTABLISH GRASSHOPPER PARITY, AND THAT SENTENCE IS A QUOTING TRAP FOR OUR METHODS.**

⚪ **1. WHAT CHANGED, AND IT IS NOT OURS.** Owner ruling `D-EU-04-F` moved `GEO-08` from **F2 (defer)** to **F4 (substitute an independent reference)**: the arc is Python-only and **no Rhino/Grasshopper runtime will ever exist**. The check is now a **second, independently written Python partitioner**, `tests/reference/geo08_reference_partitioner.py` — verified here: **standard library only** (`dataclasses`, `math`), and the single occurrence of the string `openubem` in the file is a **docstring forbidding the import**, not an import. `tests/test_eu_geo08_independent_parity.py` re-run read-only on this side: **40 passed / 0 skipped**. `eu_cell_runner.py` is **unchanged** at `1f5f6e6b…`, so nothing on the campaign path and no promoted `idf_sha256` moved.

🔴 **2. THE TRAP, AND IT IS THE ONE TO CARRY.** `GEO-08` asserts **independent-reimplementation agreement**, which is **weaker than and different from** parity with the Ankara/Grasshopper method. 🔴 **Parity with Grasshopper stays NOT TESTED and must never be written as "passed", "equivalent" or "validated against Grasshopper"** anywhere in our methods, results or captions. ⚪ The neighbourhood `.html` viewer is an **inspection aid, never evidence.** ⚪ Same class as `FINDING 174` and `RL27`: a true statement on their side that becomes a false one the moment it is quoted a level up.

⚪ **3. THEIR OWN DEFECT REPORT, RECORDED BECAUSE IT IS THE HONEST KIND.** Three latent defects were caught **in the reference** before it went green — an end-strip facade edge counted as an internal cut, a rotation-invariance tolerance tighter than float64 allows at projected-CRS magnitudes, and a convex-intersection routine with inverted half-planes returning zero for **every** overlap, which would have made the `D-EU-01` "core is additional, never carved" check **vacuous**. All three were in the reference; the implementation was not changed. ⚪ Circulation core area, shared boundary, overlap and core share of GFA were added only after their owner caught their absence — i.e. the first green was an incomplete green.

⚪ **4. ONE THING I COULD NOT VERIFY HERE, AND IT IS OUR ENVIRONMENT, NOT THEIR DEFECT.** `tests/test_eu_fold_epw_conversion.py` and `tests/test_eu_t06_weather_promotion.py` **fail to collect on this machine** — `ModuleNotFoundError: No module named 'pvlib'`. 🔴 **So no whole-suite claim about the weather path can be made from here**, and those two modules are exactly the ones covering the EPW pins that `D-S10-7` rests on. Reported to them as an environment gap on our side. 🟢 **RESOLVED, and it does not block scoring:** `pvlib >= 0.11` is a **declared dependency** of their project (`pyproject.toml:32`, verified here) and both modules pass in their venv — **our interpreter simply is not that venv.** ⚪ More importantly those two modules cover the **ERA5→EPW conversion and the T06 promotion gates**, i.e. the process that *produced* the pinned EPWs; **`D-S10-7` does not rest on them at run time.** What the runner actually checks is the frozen `weather_sha256` against the file on disk **plus** bundle-year vs EPW-year agreement, and both are asserted in `tests/test_eu_cell_runner.py` — confirmed here at lines 91/99 (wrong path, mis-hashed EPW), 249 (calendar mismatch refused) and 266 (**every fold's `bundle_year` matches its pinned EPW suffix**), all of which run without `pvlib`. 🔴 **So a scored campaign run needs no `pvlib` on this machine; if that ever changes they will say so, and then we install rather than skip.** 🟢 **GAP NOW CLOSED ON THIS MACHINE (2026-08-27, last+14, after the fact):** `pvlib 0.15.2` installed, and then `xarray`, `h5netcdf`, `cdsapi`, `ecmwf-datastores-client` — the first install was **not sufficient**, the next import error was `xarray`, so the declared list was worked through rather than guessed at. **Both modules now collect and pass: 16 passed.** ⚪ Their **whole** `tests/` tree now collects here as well — **2,378 tests** — though it was **not run** (some paths would reach EnergyPlus or the network, and running it was not asked for). 🔴 The scoping rule stands regardless: **a verification of ours is bounded to the file named**, and the run-time weather guarantee is still the four assertions in `test_eu_cell_runner.py`, not these two modules. 🔴 **No gate scored, no artefact emitted, nothing under `openubem/` written, no compute run, Speed queue EMPTY.**

---

#### 🔴 **2026-08-28 (night, last+15) — `EU-08` HAS BEEN EXECUTED FOR THE FIRST TIME. THE DRIVER IS DONE AND THE LOOP WORKS; **THE ENGINE IS NOT REPRODUCIBLE**, SO `EU-09`/`EU-10` ARE **REFUSED**, NOT PENDING.**

🟢 **1. THE DRIVER IS WRITTEN, GUARDED AND EXECUTED.** `tools/4thJ_step10_eu08_driver.py` — it owns **no physics**, calls `run_campaign_cell` once per cell, and refuses to start if any identity-bearing input is not what the ruled documents say. **Six preflight refusals, and all of them were SEEN FAILING before the driver was trusted** (10 falsifiers, 10 behaved as intended): `D1` spec digest `16d3fbd6…`, `D2` chaining-notice digest `058c9d13…` (and missing-notice), `D3` EnergyPlus version, `D4` binding digest + spec pin + fold coverage, `D5` 510 cells / es 120 · uk 180 · it 210 / `f ∈ {0, .15, .3, .5, 1}`, `D6` run order deterministic under input permutation and `cell_id` unique. ⚪ **Declared run order**, so a second implementation can reproduce it: **fold (es, uk, it) → `archetype_id` → `sensitivity_f` ascending**, which puts every `f = 0` control before its own treatment cells.

🔴 **2. `D3` IS THE GUARD THAT DECIDED THE VENUE, AND IT IS WHY THIS DID NOT GO TO SPEED.** `run_campaign_cell` **hardcodes** `energyplus_version: "23.1"` into every manifest, so **the manifest can never disagree with the binary** and the driver is the only place that disagreement is visible. **Speed carries EnergyPlus 24.2.0 only** (`~/ep_install/EnergyPlus-24.2.0-…-Linux`), has no OpenUBEM tree and no eppy/geomeppy env; submitting there would have written **`23.1` into 510 false manifests**. This machine has **23.1.0-87ed9199d4**, matching the IDF header exactly. 🔴 **So the run was executed locally and NOT via `sbatch`** — the cluster rule protects the login node, it does not require a wrong-version run. ⚪ A future Speed port needs three things and none is hard: the Linux 23.1 tarball (180 MB, downloadable), a `pip` env with `eppy`/`geomeppy`/`numpy`, and the `openubem` package — each an `sbatch` job of its own. **Not started; it was not the night's task.**

🔴 **3. FINDING 178 — `ENERGYPLUS_PATH` MEANS TWO DIFFERENT THINGS INSIDE THE SAME PACKAGE, AND THE FIRST REAL RUN DIED ON ALL 510 CELLS.** `openubem/config.py:16` treats it as a **directory** and appends `Energy+.idd`; `eu_cell_runner._run_energyplus:381` executes `str(ENERGYPLUS_PATH)` as the **binary**. The default is the directory, so every cell raised `PermissionError: [WinError 5] Access is denied` — **it was trying to execute a folder**. ⚪ Invisible to them because **every run so far was `dry_run`**, which never reaches the subprocess. 🔴 Fixed **caller-side, without touching their tree**: `ENERGYPLUS_PATH` → `energyplus.exe`, `OPENUBEM_ENERGYPLUS_IDD_PATH` set explicitly. Reported.

🔴 **4. FINDING 179 — 115 OF 510 CELLS NEVER BUILD AN IDF, AND THE LOSS IS CONCENTRATED ON `uk`.** Deterministic, identical in every run: **110 cells** raise `S0 openings require an exterior (b=1) Wall_1 host` (**22 archetypes**) and **5 cells** raise `TABULA directional window areas disagree materially with A_Window_1` (**1 archetype**) — **23 of the 102 archetypes**. 🔴 **`uk` loses 17 of its 36 archetypes**; `it` loses 4 of 42, `es` 2 of 24. Every `GB.ENG.SFH.*`, `GB.ENG.TH.*` and `GB.ENG.AB.*` in the list fails the same exterior-host check. ⚪ **The fold is the cross-validation axis**, so an uneven loss is not a cosmetic one: if this is a true data property rather than an over-strict check, **the `uk` fold of this campaign is not usable as it stands**. Engine-side, reported, **not ours to fix**.

🔴 **5. FINDING 180 — THE BLOCKING ONE: ENERGYPLUS RETURNS DIFFERENT ANSWERS FOR THE SAME IDF.** `uk__GB.ENG.MFH.02.Gen.ReEx.001.001__f050`, one IDF, one EPW, `energyplus.exe -x -r` run **three times by hand** into three empty directories → **three different `eplusout.csv` digests**. Two campaign runs disagreed by **27.1 %** on that cell (74253.89 vs 54094.73 kWh) while the IDFs were **byte-identical apart from the absolute `Schedule:File` path** and the `gain_csv` md5s were **equal** — so nothing upstream of EnergyPlus differed on either side. 🔴 **The `.err` file names the cause itself: `** Warning ** This building has no thermal mass which can cause an unstable solution.`** Three more warnings agree — `GetVertices: Floor is upside down! Tilt angle=[0.0], should be near 180`, `CalculateZoneVolume: 1 zone is not fully enclosed`, `GetSurfaceData: Entered Zone Floor Area(s) differ more than 5% from the sum of the Space Floor Area(s)`. A massless, unenclosed zone with an inverted floor **does not have a single answer**, so the `SolveForWindowTemperatures` fatals are a **symptom, not the disease**. 🔴 **Every one of these is a Warning, not a Severe** — no suite on either side could have caught it, and the `dry_run` path never reaches it.

🔴 **6. THE SCALE, MEASURED OVER THREE FULL 510-CELL RUNS — THIS IS THE NUMBER TO QUOTE.** **264** cells complete in all three · **115** refuse in all three · **1** fails in all three · **130 CHANGE STATUS between runs** · and **132 of the 264 always-completing cells return a DIFFERENT heating value**, worst case **27.1 %**. ⚪ **Concurrency is ruled out**: two **serial** (`--workers 1`) runs flipped a cell from 209194.35 kWh to a fatal, and the by-hand triple-run used no driver at all. 🔴 **A campaign whose completed set moves by 130 cells between runs has no denominator, and a mean over a set that changes is not a measurement.**

🔴 **7. `EU-09` / `EU-10` ARE REFUSED, NOT PENDING — AND THAT IS A DELIBERATE CHOICE, NOT AN OMISSION.** Scoring this campaign would produce a number that changes when it is re-run. 🔴 **No gate was scored; no band, threshold, verdict or count moved.** ⚪ **The loop side will not need to change when the engine does**: the driver re-runs against the same digests, so the day OpenUBEM closes `FINDING 180` this is one command, not a rebuild.

⚪ **8. WHAT MOVED.** New: `tools/4thJ_step10_eu08_driver.py`; `messages_OpenUBEM/2026-08-27_4J_to_OpenUBEM_eu08_first_execution_and_engine_nondeterminism.md` (copied to their inbox); run trees under `GSSCanada/_local_runs/` (`4J_eu08_campaign_2026-08-27`, `_repro_B`, `_repro_C`, `_dryrun`, `eptest2`, `eptest3`) with a `campaign_summary.json`, per-cell manifests and per-cell `eplusout.err` for every cell. Modified: this file and `Prompts/RESUME.md`. 🔴 **Nothing under `openubem/` written; no promoted artefact edited; `v1.1`, `binding_v2` and the `10.1` notice all opened read-only and re-verified by digest at the start of every run; no job submitted and the Speed queue is EMPTY.** ⚠ **The board is still NOT re-published** and has no card for the driver, the campaign or `FINDING 178/179/180`.

🔴 **What is owed to a person.** ⚪ **Nothing is waiting on the author tonight** — the block is engine-side and it is OpenUBEM's. ⚪ Owed by **OpenUBEM**: `FINDING 180` first (the massless / unenclosed / inverted-floor box), then `FINDING 179` (the 23 archetypes, `uk` worst), then `FINDING 178` (the `ENERGYPLUS_PATH` split), plus the `completed: bool` field request. ⚪ Owed by **us the day the engine is fixed**: re-run the driver — **one command** — then `EU-09`/`EU-10` scoring. ⚪ Still the author's, unchanged and untouched: **`D-S6-16` (a′) or (c′)**, the **`D-S8-3` follow-on**, the **`D-S8-4` follow-on**. ⚪ Optional: **Fuentes et al. (2018)**.

---

#### 🔴 **2026-08-28 (night, last+16) — OPENUBEM FIXED THE CAUSE OF `FINDING 180` WITHIN THE HOUR AND THE FIX IS REAL, BUT **THE CAMPAIGN IS STILL NOT REPRODUCIBLE**. `136 OF 510` CELLS SURVIVE THREE RUNS, `es` CONTRIBUTES **ZERO**, AND ONLY **5 ARCHETYPES** HAVE ALL FIVE `f` LEVELS. `EU-09`/`EU-10` STAY REFUSED.**

🟢 **1. THEIR FIX, VERIFIED HERE BEFORE IT WAS USED.** `FINDING 180`'s cause was **theirs and mechanical**: `_build_idf` emitted the S0 equivalent envelope and **never added the `InternalMass` object**, while the envelope is `Material:NoMass` throughout — so the zone had **literally zero heat capacity**, exactly as the `.err` said. `scripts/run_eu_s2_campaign.py:244` had always added it; the cell runner omitted it. Runner now `82eb7cf252fcf4a83390cf4506cfda80c0d21ce535d41dd2dffd7ab22169beb6`, **30 tests pass** (re-run here, read-only), `add_european_internal_mass` at line 340. ⚪ They also fixed `FINDING 178` — and the right way round: **every other consumer in their repo reads `ENERGYPLUS_PATH` as the install directory**, so the cell runner was the sole outlier and it moved, not the convention. And they added **`completed` (bool) + `completion_status`** to the manifest, which was our §6 field request. 🔴 **The driver is re-pinned to their digest and now reads `completed` rather than deriving it**, keeping the local derivation only as a fallback for an older runner.

🟢 **2. THE SINGLE-CELL CHECK THEY ASKED FOR PASSED, EXACTLY.** Three serial runs of rank-0: **177928.78032852308 kWh, identical to the last digit, three times.** ⚪ Their own re-test of our flipping `uk` cell gave 76524.88906116915 three times against our 74253.89 / 54094.73 / fatal.

🔴 **3. AND THE CAMPAIGN IS STILL NOT REPRODUCIBLE — 333 / 346 / 348 COMPLETED ACROSS THREE FULL 510-CELL RUNS.** So the massless box was **a** cause and not **the** cause. 🔴 **`FINDING 181` — A CELL CAN FINISH WITH RETURN CODE 0 AND BE NUMERICALLY MEANINGLESS, AND `completed: true` CANNOT SEE IT.** EnergyPlus reports a diverging heat balance as a **Warning**: `Temperature out of range [-100. to 200.] (PsyPsatFnTemp)` and `Inside surface heat balance did not converge with Max Temp Difference [C] =10.088`; it only escalates to a Severe when a surface leaves the solver's bounds entirely (`CalcHeatBalanceInsideSurf: The temperature of -76844.75 C`). ⚪ **A run that lands just inside the bound is reported completed and carries a heating figure no downstream gate would question.** 🔴 So **`completed` is necessary and not sufficient**, and the driver now screens `eplusout.err` itself and records `unstable_solution` per cell — loop-side, because nothing downstream of it can see the `.err`.

🔴 **4. THE NUMBERS TO QUOTE, THREE RUNS, SAME DIGESTS THROUGHOUT — AND NOTHING ELSE.**
```
completed                          333 / 346 / 348
of those, unstable_solution         97 / 102 /  94
clean (completed, no marker)       236 / 244 / 254
clean in ALL THREE runs                          185
of those, heating STILL differs across runs       49     (max 45.5 %)
CLEAN AND BIT-REPRODUCIBLE IN ALL THREE           136     of 510
refused at IDF build, every run                   115     (FINDING 179, unchanged)
```
🔴 **Two facts inside that table matter more than the headline.** ① **`es` contributes ZERO to the reproducible set** — every completed `es` cell in every run carries an out-of-range temperature warning, so **the Madrid fold is currently unusable, not merely reduced**; the 136 are `uk` 63 · `it` 73. ② Of the 136, **only 5 archetypes have all five `f` levels reproducible**. 🔴 **The sensitivity design compares `f` levels WITHIN an archetype, so `5 of 102` is the number that decides whether anything can be said — not the 136, and never the 348.**

🔴 **5. `EU-09` / `EU-10` STAY REFUSED, AND THAT IS THE FINDING, NOT AN OMISSION.** A campaign whose completed set moves by ~15 cells and whose values move by up to 45.5 % between identical runs **has no denominator**, and a mean over a set that changes is not a measurement. 🔴 **No gate was scored; no band, threshold, verdict or count moved.** ⚪ OpenUBEM has raised **`D-EU-26`** on `FINDING 179` (A relax the exterior-host check / B accept 395 of 510 with the `uk` fold 47 % incomplete / C successor work package) — **their owner's, and we do not rule on it**; we did offer that a **per-archetype completeness requirement** is a cheaper filter than any count of manifests, and that the two `.err` strings above are a better gate than either.

⚪ **6. WHAT MOVED, AND WHAT IS NOW STALE.** Modified: `tools/4thJ_step10_eu08_driver.py` (runner digest re-pinned; reads `completed`; new `UNSTABLE_MARKERS` screen and `n_completed_but_unstable` / `n_completed_and_stable` / `unstable_cells` in the summary), this file, `Prompts/RESUME.md`. New run trees `_local_runs/4J_eu08_v4_{T1,T2,T3}` (**the ones to read**), plus `v3_*`, `v2_*`, `det_*`, `eptest4`. 🔴 **EVERY `idf_sha256` AND EVERY HEATING VALUE FROM THE FIRST CAMPAIGN (`4J_eu08_campaign_2026-08-27`, `_repro_B/C/D`) IS SUPERSEDED** — the `InternalMass` fix changes every IDF. They are kept for the audit trail and **must never be quoted**. ⚪ Nothing published moves, because **nothing from any of these runs was ever scored.** 🔴 **Nothing under `openubem/` written; no promoted artefact edited; no job submitted and the Speed queue is EMPTY.** ⚠ **The board is still NOT re-published.**

🔴 **What is owed to a person.** ⚪ **Nothing is waiting on the author** — every open item is engine-side and OpenUBEM's. ⚪ Owed by **OpenUBEM**: the residual instability behind `FINDING 181` (the `es` fold first — it is 100 % affected), then their owner's ruling on **`D-EU-26`**. ⚪ Owed by **us the day those close**: re-run the driver — **one command, `--workers 14`, ~80 s** — then `EU-09`/`EU-10`. ⚪ Still the author's, unchanged and untouched: **`D-S6-16` (a′) or (c′)**, the **`D-S8-3` follow-on**, the **`D-S8-4` follow-on**. ⚪ Optional: **Fuentes et al. (2018)**.

---

#### 🔴 **2026-08-28 (night, last+17) — THE `5 OF 102` ARCHETYPES ARE LISTED, AND THE LIST CARRIES A WORSE FACT THAN THE COUNT: ACROSS THE WHOLE `f` SWEEP THE HEATING MOVES BY **0.11–0.39 %**, TWO ORDERS OF MAGNITUDE BELOW THE `45.5 %` RUN-TO-RUN NOISE.**

⚪ **1. WHY THIS WAS MEASURED.** OpenUBEM asked for the one next measurement that does **not** presume their owner's `D-EU-26` ruling: *which archetypes have all five `f` levels clean, listed* — five being small enough that the list itself is the result. Read-only over the existing `_local_runs/4J_eu08_v4_{T1,T2,T3}` trees; **no run re-executed, no gate scored, nothing under `openubem/` touched.** Definition used: `status == OK` **and** `unstable_solution == false` in all three runs **and** `heating_kwh` identical across the three.

🔴 **2. THE FIVE.** `uk` 2 · `it` 3 · **`es` 0**. All five are `Gen.ReEx.001.001`.
```
it  IT.MidClim.AB.03.Gen.ReEx.001.001    233397.078476 -> 232891.815003   0.2170 %
it  IT.MidClim.MFH.01.Gen.ReEx.001.001    86134.906189 ->  85803.252495   0.3865 %
it  IT.MidClim.SFH.08.Gen.ReEx.001.001     8646.078301 ->   8657.420097   0.2638 %
uk  GB.ENG.AB.04.Gen.ReEx.001.001        433376.025339 -> 432845.507279   0.1226 %
uk  GB.ENG.MFH.02.Gen.ReEx.001.001        76609.278498 ->  76524.889061   0.1103 %
```
(`f000 -> f100`, spread over the five levels.) ⚪ Monotone decreasing on four of five; `IT.MidClim.SFH.08` and `GB.ENG.MFH.02` **turn back up at `f100`**, so at this magnitude the effect is not even monotone.

🔴 **3. THE FACT THAT MATTERS.** 🔴 **The signal the sensitivity design exists to detect is `0.11–0.39 %`, while the run-to-run spread on the 49 cells that were clean in all three runs and still moved is up to `45.5 %`.** So the effect sits **two orders of magnitude below the current noise floor**. ⚪ Consequence for the ruling: **a `D-EU-26` outcome that recovers cells without also closing `FINDING 181` would not make `EU-09` scoreable** — the denominator would grow and the noise would not shrink. 🔴 **This is NOT recorded as a finding about `f`**: five archetypes is not a population, the pathway is heating-only, and the whole set is one construction variant. It is a statement about the measurement, not about the physics.

⚪ **4. COMPLETENESS HISTOGRAM, offered to OpenUBEM as an ex-ante check on `D-EU-26`.** Of the **42** archetypes with any reproducible cell: **5** have all five `f` levels, **16 have four**, 7 three, 12 two, 2 one. 🔴 **Sixteen archetypes are ONE CELL SHORT**, which is the cheapest place a partial fix would show up — whichever option the owner takes, that number should move first.

⚪ **5. WHAT WAS ACCEPTED FROM THEIR SIDE, AND WHAT MUST NOT BE RE-TRIED.** 🔴 **The S0 floor-flip is REVERTED and must not be re-attempted without new evidence** — flipping the upside-down floors cleared `GetVertices: Floor is upside down!` and turned a bit-stable `es` cell into **1 fatal in 3** (`Convergence error in SolveForWindowTemperatures`); they recorded the measurement so nobody repeats it. ⚪ Our rank-0 cell reproduces on their machine to the last digit (`177928.78032852308`) **and is one of our unstable ones** — a cell can be bit-stable and still meaningless, which is the argument for **screening** rather than repeating runs. ⚪ Their reading of what remains: the S0 zone is **deliberately unenclosed** (TABULA's separately declared areas cannot close a prism without changing a source quantity), so `FixViewFactors: View factors not complete` and the `OtherSideCoefficients` window hosts make the interior radiant exchange **ill-posed by construction** — i.e. a property of the equivalent-envelope method, **a DESIGN question, their owner's, recorded as T08 alongside `D-EU-26`**, and **we do not rule on it**.

🔴 **6. ONE FRAMING RULE FOR ANYTHING WRITTEN.** **`es` = 0 is a statement about the equivalent-envelope method as currently emitted, NOT about Madrid.** The ES ingestion, the weather bundle, the presence bundle and the `D-EU-22` coverage work are **not** in question and must never be implicated by the phrasing.

⚪ **7. STATE.** Unchanged from `last+16`: nothing waits on the author; owed by OpenUBEM is `FINDING 181` (`es` first, 100 % affected) then the owner's `D-EU-26` ruling; owed by us the day those close is **one command, `--workers 14`, ~80 s**, then `EU-09`/`EU-10`. ⚠ **The board is still NOT re-published.** 🔴 **No file under `openubem/` written, no promoted artefact edited, no job submitted, Speed queue EMPTY.**

⚪ **8. ADDENDUM TO THIS ENTRY (same night, after OpenUBEM's reply) — ONE CONSTRAINT ON THE RE-RUN, AND ONE SHARPENING.** 🔴 **The re-run happens ONCE, after BOTH `FINDING 181` and `D-EU-26` are settled — never once per ruling.** Three partially-superseding campaigns would leave a later reader unable to tell which `idf_sha256` was current, and the tree already carries one superseded campaign for exactly that reason. ⚪ Their framing, kept because it is better than ours: **all five archetypes are `Gen.ReEx.001.001` — one construction variant — so the five are LESS independent than "five archetypes" reads.** ⚪ `D-EU-26` now carries the stability question as its own **§6** rather than beside it, with the ordering stated to the owner: **the ruling decides how many cells are *attempted*; `FINDING 181` decides whether an attempted cell *means* anything; only the second is binding on scoreability.** ⚪ Their side: suite green **2,341 passed / 55 skipped**, the only change under `openubem/` remains the T07 runner fixes, `european_box.py` clean, floor flip reverted, nothing running. ⚪ Recorded there as **T09** and in `D-EU-26` §6.
