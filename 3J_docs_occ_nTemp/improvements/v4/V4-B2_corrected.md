# V4-B2 (corrected half) — the measured Leg-2 office EUI, all 252 published runs

**2026-08-06 · retrieval only · `scp` → local `sqlite3` → delete → next · peak local disk one file.
No `sbatch`, no `srun`, no `python` on the login node, no simulation cell.**
Generator: `b2_office_corrected.py` · retrieval loop: `scratchpad/b2sql/pull_office.py` ·
per-run record: `v4_b2_office_factors.jsonl` · result: `v4_b2_office_corrected.json`.

**Predecessor:** `V4-B2_defect_reach.md`, whose §3 could only *bracket* these four rows and whose §4
reported them BLOCKED. **Both are superseded on the office half only — and §4's premise was a rule the
user changed, not a transfer that failed.** §2's warning that a residential factor says nothing about
an office building is **not** superseded; it is confirmed below.

---

## 0. 🔴 The disclosure statement for the submitted 2J paper

> **The four office EUI values published in the 2J manuscript (172.7 / 172.6 / 172.5 / 172.7 kWh/m²)
> are inflated by a units-conversion defect: `calculate_eui()` selects the `End Uses By Subcategory`
> table without filtering `ReportName`, so EnergyPlus's peak-demand copy of that table — reported in
> **W** — is summed as though it were **kWh**. Re-reading all 252 published simulation results with
> `ReportName` pinned to the annual-energy report gives 106.6 / 106.7 / 106.7 / 106.6 kWh/m². The
> inflation factor is **not a constant**: measured across those 252 runs it ranges **1.518 to 1.908**,
> because it is the ratio of a building's peak demand to its annual energy and therefore depends on
> the building and the climate zone. **No single divisor corrects the published table.** The four
> office values remain inside the reference band [100, 200] kWh/m² after correction, so no office
> verdict changes; the values themselves are **≈38 % lower** than published.**

⚠️ ~~**This statement covers the office rows only.** The four residential rows are the subject of
`V4-B2_PREREGISTRATION_resid_sample.md` and are measured separately; **the disclosure is not complete
until that half is in**, and §3 of `V4-B2_defect_reach.md` predicts at least two of them do move
out of band. **Do not send this paragraph on its own.**~~

### 🟢 The residential half landed the same day. The complete statement is below; the one above is superseded.

> **All eight EUI values published in the 2J manuscript are inflated by unit-handling defects in
> `calculate_eui()` (`Step8_docs/eSim_bem_utils_3J/plotting.py`). There are two defects, and they are
> complementary — which one fires depends on whether EnergyPlus wrote the run in SI or IP units.
> (i) The `End Uses By Subcategory` table is selected without filtering `ReportName`, so the
> peak-demand copy of that table is summed into the annual total; in SI output its units are **W** and
> are added as **kWh**. (ii) The water-exclusion guard tests only for `m3`, so in IP output the water
> rows — reported in **gal** and **gal/min** — are also added as **kWh**. Re-reading every published
> simulation result with `ReportName` pinned to the annual-energy report and all volume and power
> units excluded gives:**
>
> | published row | n | published | **corrected** | band | published verdict | **corrected verdict** |
> |---|--:|--:|--:|---|---|---|
> | office, all | 252 | 172.7 | **106.56** | [100, 200] | IN | IN |
> | office, Knowledge | 84 | 172.6 | **106.66** | [100, 200] | IN | IN |
> | office, Public | 84 | 172.5 | **106.71** | [100, 200] | IN | IN |
> | office, Sales | 84 | 172.7 | **106.56** | [100, 200] | IN | IN |
> | resid `MidRise` | 100* | 177.5 | **128.21** | [111.1, 216.7] | IN | IN |
> | resid `HighRise` | 100* | 143.0 | **101.23** | [113.9, 147.2] | IN | 🔴 **BELOW** |
> | resid `OtherDwelling` | 100* | 140.0 | **124.98** | [136.1, 186.1] | IN | 🔴 **BELOW** |
> | resid `SingleD` | 100* | 211.7 | **130.57** | [130.6, 186.1] | **ABOVE** | 🔴 **no longer ABOVE; BELOW-or-IN undetermined** |
>
> **\*** The four office rows are the complete published population (252 runs, all re-read). The four
> residential rows are a **pre-registered random sample of 100 runs each** drawn from populations of
> 2 100; their corrected values carry exact distribution-free 95 % intervals of 99.38–104.77
> (`HighRise`), 125.05–131.18 (`MidRise`), 121.56–130.42 (`OtherDwelling`) and 126.60–134.86
> (`SingleD`). **`SingleD` misses its floor by 0.03 kWh/m² inside an 8.3-wide interval, so its
> corrected verdict is undetermined between BELOW and IN; what is determined is that it is no longer
> above the ceiling.**
>
> **The inflation is not a constant and cannot be divided out.** Across the 252 office runs the factor
> ranges 1.518–1.908, tracking the building and the climate zone rather than the occupancy scenario.
> Across the residential runs it ranges 1.0005–1.754, separating by unit system rather than by
> archetype. **No single divisor corrects the published table.**
>
> **Three of the eight published verdicts change.** Two residential values published as within their
> reference bands fall below them, and the single WARN in the published table — raised because
> `SingleD` exceeds the SHEU ceiling — describes a condition that is not present in the corrected
> value. **The office rows are unaffected in verdict; their values are ≈38 % lower than published.**
> Scenario-comparison directions in the office section are preserved for every comparison larger than
> 1.13 kWh/m², but **absolute effect sizes quoted in kWh/m² are overstated by roughly two thirds.**

⚠️ **What this statement does not do:** it does not choose between an erratum and a re-publication.
That was reserved for the user in §4.3 and is still theirs. It supplies the magnitude, the mechanism,
and which conclusions move.

---

## 1. The guard, checked before any corrected number was read

Step 9's `build_eui()` takes the **median** of `eui_kWh_m2` over the office runs, once for `all` and
once per subtype. That arithmetic is reproduced here on **both** columns. The shipped column must
come back as the published table, or this is not the published population.

| published row | n | shipped median | published | match |
|---|--:|--:|--:|:--|
| office all | 252 | **172.66** | 172.7 | ✅ |
| office Knowledge | 84 | **172.62** | 172.6 | ✅ |
| office Public | 84 | **172.54** | 172.5 | ✅ |
| office Sales | 84 | **172.72** | 172.7 | ✅ |

✅ **All four reproduce to the published rounding.** Two further independent agreements: the band
`[100, 200]` and the four published values were read from **Leg-2's own scorer and output CSV**
(`3rdJ_09_activityDrivenLoads_2split.py:50`, `outputs_step9/step9_eui_by_channel.csv` rows 6–9), not
copied out of `V4-B2_defect_reach.md` — a check whose two inputs share an ancestor cannot catch a
value that is wrong in both. **And that CSV carries `n = 252 / 84 / 84 / 84`, which is exactly what the
retrieval hit without being told.** The retrieval covered **252 of 252** runs;
3 fetches failed on a first pass (`scp rc=255`, caused by a second retrieval running concurrently —
Speed refuses the parallel connection) and **all 3 were retrieved on the retry**. **Nothing is
missing, and nothing is estimated.**

---

## 2. The corrected table

| published row | n | published | **corrected** | band | published verdict | **corrected verdict** |
|---|--:|--:|--:|---|---|---|
| office all | 252 | 172.7 | **106.56** | [100, 200] | IN | **IN** |
| office Knowledge | 84 | 172.6 | **106.66** | [100, 200] | IN | **IN** |
| office Public | 84 | 172.5 | **106.71** | [100, 200] | IN | **IN** |
| office Sales | 84 | 172.7 | **106.56** | [100, 200] | IN | **IN** |

🟢 **The office half survives correction. No published office verdict moves.** `V4-B2_defect_reach.md`
§3 said these four *"depend on the factor"* and could not say which way. **Measured: they stay in.**

🔴 **But they survive with 6.6 kWh/m² of clearance on a 100 floor, and the runs behind the median
straddle it.** Per-run corrected EUI spans **93.51 – 117.91**, and **50 of 252 runs (19.8 %) fall below
the floor.** The median passes; a fifth of the population does not. **Reported because it is true, not
because it changes the verdict** — under the `all_cells` rule Leg-3 uses for office (V2-B3), this
population would not pass at all. Leg-2 scored the median, and that is the rule this table is scored
under.

---

## 3. Uniformity, refuted again and harder

| | min | median | max | spread |
|---|--:|--:|--:|--:|
| 12 local residential smoke cells (`V4-B2_defect_reach.md` §2) | 1.4868 | — | 1.7601 | 18.4 % |
| **252 published office runs (measured here)** | **1.5182** | **1.6514** | **1.9075** | **25.6 %** |

> 🔴 **Added later the same day:** the top row is **not** "the residential range". All 12 of those
> cells are SI files, and the residential campaign's real range is **1.0005 – 1.7541 (75.3 %)**,
> because `SingleD` and `OtherDwelling` sit at ~1.002. **The office comparison below is unaffected** —
> office is entirely SI, so 1.4868–1.7601 is the right thing to have compared against. But the row is
> mislabelled and is corrected here rather than deleted.

**The office range runs past the top of the residential range.** A divisor taken from residential cells
(1.706 was the number originally proposed) would have under-corrected the worst office runs by 12 %.
**`172.7 ÷ 1.706 = 101.2` — inside the band by 1.2 kWh/m². The measured answer is 106.56.** The right
answer and the shortcut happen to agree on the *verdict* and disagree on the *number* by 5 %; the
shortcut had no way to know that, which is the whole argument against it.

### What the factor actually tracks — and what it does not

| grouping | factor range within the group |
|---|---|
| **by occupancy scenario** (7 levels, n=36 each) | medians **1.6488 – 1.6550** — a **0.4 %** spread |
| by building (`Tall` / `SuperTall`) | 1.5896 / 1.6942 medians, ranges overlap |
| **by climate zone** (6 levels, n=42 each) | medians **1.5708 (5C) → 1.8465 (7A)**, a **17.6 %** spread |
| **within a single cell** (same building, same climate, 7 scenarios) | **0.0033 – 0.0137** absolute |

🔴 **The contamination is a function of the building and the weather. The occupancy scenario moves it
by essentially nothing.** Within one cell the factor is constant to ~1 %; across climate zones it moves
18 %. That is exactly what a peak-demand-to-annual-energy ratio should do, and it is the mechanism
named in `V4-B2_defect_reach.md` §2 — now measured on the channel it was doubted for.

---

## 4. What this does to Leg-2's scenario comparisons

Not pre-registered — measured after the corrected column existed, and labelled as such.

Because the factor is near-constant *within* a cell, the correction is close to a uniform rescaling of
the seven scenarios in that cell. Testing every scenario pair inside every cell (**756 comparisons**):

- **113 comparisons (15 %) change sign** after correction.
- **Every one of them has a shipped gap ≤ 1.13 kWh/m²** (median gap **0.20**).
- **128 comparisons have a shipped gap larger than 1.13, and not one of them flips.**

⇒ **No scenario comparison large enough to have been claimed changes direction.** The flips are all
inside a sub-1.2 kWh/m² band that was never a result.

⚠️ **This is not a clean bill of health.** Where the sign holds, the **magnitude does not**: a scenario
difference quoted in kWh/m² is inflated by the same ~1.65× as the levels. **Any absolute effect size in
the office section is overstated by about two thirds.**

---

## 5. `V4-B2_defect_reach.md` §5 — the open question, answered

§5 recorded a puzzle: the three subtype medians differ by **0.2 kWh/m² (0.12 %)** across three
different occupancy profiles, and offered two untested candidates — *the subtypes genuinely differ very
little*, or *the demand term swamps the schedule differences*.

**Measured:** the corrected subtype medians spread **0.144 kWh/m²**; the shipped ones spread **0.182**.
**Removing the contamination does not open the gap — it narrows it slightly.**

⇒ 🔴 **The second candidate is dead. The tightness is not a contamination artefact.** The three office
subtypes genuinely produce near-identical annual EUI in this model. **That is a finding about the
model, not about the defect**, and it belongs to whatever asks why three distinct occupancy profiles
land within 0.14 kWh/m² of each other. **Recorded, not explained here.**

---

## 6. What did not change

- **Nothing in `Leg2_2-split/` was written to.** No published file was edited, no manuscript text
  touched.
- **The erratum-versus-re-publication choice is still the user's**, as §4.3 reserved it. This document
  supplies the magnitude for the office half and nothing else.
- ~~**`V4-B2_defect_reach.md` §2 and §3 stand for the residential rows.** They are brackets, not
  corrections, until the pre-registered sample lands.~~
  🔴 **CORRECTED the same day — the sample landed and knocked them down.** §3's residential brackets
  are **withdrawn**, not merely superseded: they applied a factor of 1.49–1.76 to `SingleD` and
  `OtherDwelling`, whose runs have a measured factor of **1.002**. §2's *range* is unrepresentative —
  all 12 of its cells are SI files, and the two IP archetypes behave nothing like them. **§2's
  mechanism survives; its numbers do not.** See `V4-B2_corrected_resid.md` and
  `V4-B2_defect_reach.md` §8.

## 7. Reopen trigger

**Reopens if** the office subtype definitions, the band, or the `median`-versus-`all_cells` scoring
rule for Leg-2 office changes — under `all_cells` this population **fails**, and that is a live
difference between Leg-2's rule and Leg-3's. **Also reopens** if the residential sample shows the
factor varying with the **occupancy scenario** rather than with the building and the climate — that
would falsify the mechanism named in §3, and the office numbers would need re-reading under whatever
replaces it.

⚠️ **Deliberately not stated here: a numeric bound taken from the residential range.** That sample is
running under its own pre-registration (`V4-B2_PREREGISTRATION_resid_sample.md`) and **quoting a
partial-sample number back into this document would contaminate it.** The residential range goes in
that document, after its three predictions are scored.

⚠️ **Not a reopen trigger:** wanting a rounder number. **The corrected office values are 106.56 /
106.66 / 106.71 / 106.56 and are not to be re-derived by dividing the published ones.**
