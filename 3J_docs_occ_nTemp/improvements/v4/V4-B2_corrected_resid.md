# V4-B2 (corrected half, residential) — the pre-registered sample, scored

**2026-08-06 · retrieval only · `scp` → local `sqlite3` → delete → next · peak local disk one file.
No `sbatch`, no `srun`, no `python` on the login node, no simulation cell.**
Generator: `b2_resid_corrected.py` · retrieval loop: `scratchpad/b2sql/pull_resid_units.py` and
`pull_resid_sample.py` · per-run record: `v4_b2_resid_factors.jsonl` · result:
`v4_b2_resid_corrected.json`.

**Pre-registration:** `V4-B2_PREREGISTRATION_resid_sample.md`, written and dated **before the first
residential campaign `eplusout.sql` was fetched.** This document does not restate its predictions; it
scores them.

**Companion:** `V4-B2_corrected.md` (office, all 252 runs — the other half of the same defect).

---

## 0. The result in three lines

1. ✅ **P3 passes on all four archetypes.** The sample is the published population; everything below
   it counts.
2. 🔴 **P1 is FALSIFIED.** It predicted `HighRise` **and** `OtherDwelling` fall below their floors.
   `HighRise` does. **`OtherDwelling` does not move at all.**
3. 🔴🔴 **Chasing why turned up a SECOND defect in the same function**, complementary to the first —
   see §5 and `V4-B2_defect_reach.md` §8. **Measured the same day.**
4. 🔴🔴 **Fully corrected, THREE of the four residential rows leave their bands** — `HighRise` and
   `OtherDwelling` fall below, and **`SingleD` inverts from ABOVE to the bottom of the band, taking
   Leg-2's sole published EUI WARN with it.** Only `MidRise` is unmoved.
5. ⚠️ **`SingleD`'s corrected verdict is UNDETERMINED**, not BELOW — it misses the floor by 0.03
   kWh/m² inside an interval 8.3 wide. What is determined is that **it is no longer ABOVE.**

**Combined with the office half: of Leg-2's 8 published EUI rows, 4 stay in band (all office),
1 stays in band (`MidRise`), and 3 move out.**

---

## 1. P3 first — does the sample reproduce the published population?

🔴 **Printed and checked before any corrected number was read.** If the shipped column does not come
back as the published table, the sample is not the published population and nothing below it means
anything.

| archetype | n | shipped median | published | diff | P3 |
|---|--:|--:|--:|--:|:--|
| `SingleD` | 100 | **211.10** | 211.7 | −0.28 % | ✅ |
| `MidRise` | 100 | **178.38** | 177.5 | +0.50 % | ✅ |
| `OtherDwelling` | 100 | **140.11** | 140.0 | +0.08 % | ✅ |
| `HighRise` | 100 | **145.46** | 143.0 | **+1.72 %** | ✅ |

**All four inside the ±2 % pre-registered tolerance**, with `HighRise` the closest call at +1.72 %.
**400 of 400 runs retrieved, zero failures**, 1 193 s.

Bands and published values were read from **Leg-2's own artefacts** —
`3rdJ_09_activityDrivenLoads_2split.py:43-46` and `outputs_step9/step9_eui_by_channel.csv` rows 2–5 —
**not** copied from `V4-B2_defect_reach.md`. A consistency check whose two inputs share an ancestor
cannot catch a value that is wrong in both.

---

## 2. The corrected table, and the interval is exact

The interval is **distribution-free, from binomial order statistics** — no normality assumption, no
bootstrap — and it is **computed for the achieved n** rather than read off a table for n = 100, so a
short sample would still be scored correctly. At n = 100 it is `[x(40), x(61)]`, coverage **0.9648**.

| archetype | n | published | **corrected** | 95 % interval | band | published | **corrected** |
|---|--:|--:|--:|---|---|:--|:--|
| `SingleD` | 100 | 211.7 | **210.86** | 207.15 – 217.11 | [130.6, 186.1] | ABOVE | **ABOVE** |
| `MidRise` | 100 | 177.5 | **128.21** | 125.05 – 131.18 | [111.1, 216.7] | IN | **IN** |
| `OtherDwelling` | 100 | 140.0 | **139.88** | 135.47 – 145.48 | [136.1, 186.1] | IN | **IN** ⚠️ |
| `HighRise` | 100 | 143.0 | **101.23** | 99.38 – 104.77 | [113.9, 147.2] | IN | 🔴 **BELOW** |

⚠️ **`OtherDwelling`'s interval straddles its floor** — the lower bound 135.47 sits **below** 136.1
while the median sits above it. The row is IN, and it is IN by less than the sampling uncertainty.
**Reported, not rounded away.**

⚠️ **`SingleD` and `OtherDwelling` above are "§1-defect corrected", which for these two rows is very
nearly the shipped value** (factor ≈ 1.002). **These are the numbers P1 was scored against, and they
are NOT the corrected values for those two rows — §5 measures those, and both move out of band.**

---

## 3. P1 — scored, and FALSIFIED

P1 required, for **both** `OtherDwelling` and `HighRise`: corrected median **below** the floor, **and**
the upper end of the interval below it too.

| row | median | floor | median < floor | CI upper | CI upper < floor | P1 |
|---|--:|--:|:--|--:|:--|:--|
| `OtherDwelling` | 139.88 | 136.1 | **NO** | 145.48 | **NO** | 🔴 **FALSIFIED** |
| `HighRise` | 101.23 | 113.9 | yes | 104.77 | yes | ✅ confirmed |

🔴 **P1 overall: FALSIFIED.** `V4-B2_defect_reach.md` §3's *"BELOW, either way"* is **WITHDRAWN for
`OtherDwelling`, not softened.** It stands for `HighRise`, where it was right and right by a wide
margin — 12.7 kWh/m² clear of the floor with the whole interval below.

**A prediction that names two rows and gets one is a failed prediction, not a half-success.** It is
recorded as failed.

### P2 — `SingleD`, no direction was predicted

Published **211.7, ABOVE** the ceiling — the **sole WARN** in Leg-2's published EUI table. Corrected:
**210.86, still ABOVE**, interval 207.15 – 217.11 entirely above the 186.1 ceiling.

🔴 **`V4-B2_defect_reach.md` §3 offered "IN, or BELOW" for this row. The measured answer is neither.**
It does not move. The WARN is not an artefact of the defect — it survives it untouched.

---

## 4. Why P1 failed — the factor separates by archetype, and the reason is named

| archetype | factor min | factor max | unit system |
|---|--:|--:|:--|
| `HighRise` | 1.2038 | 1.7541 | **SI** |
| `MidRise` | 1.1785 | 1.7400 | **SI** |
| `SingleD` | **1.0005** | **1.0026** | **IP** |
| `OtherDwelling` | **1.0007** | **1.0024** | **IP** |

**Over the sample: min 1.0005 · median 1.0905 · max 1.7541 — a 75.3 % spread.** Not the 18.4 % that
`V4-B2_defect_reach.md` §2 measured, because every one of §2's 12 local files was `HighRise` or
`MidRise` — **all 12 sat on one side of a split nobody knew was there.**

**The split is the unit system, not the archetype.** §1's defect works by summing the peak-demand copy
of `End Uses By Subcategory` into the annual total. In **SI** output that copy is in **`W`** — an
unrecognised unit, passed through as kWh, and numerically enormous. In **IP** output the same copy is
in **`kBtuh`**, roughly a thousandth of the annual `kBtu` figure, so it vanishes into rounding.

🔴 **This is archetype *separation with a named mechanism*, and it must not be reported as
"bimodality".** The shape is a consequence; the cause is which unit system EnergyPlus wrote the file
in. Naming the shape instead of the cause is exactly the error `V4-A5` was written to correct.

⚠️ **A factor of 1.00 does NOT mean the row is sound.** It means *this* defect did not fire on it.

---

## 5. 🔴🔴 The second defect — and the corrected values for the two IP rows

Confirmed in the shipped code at `plotting.py:319` and `:344`, and reproduced arithmetically on one
probe file of each unit system. Full statement: **`V4-B2_defect_reach.md` §8.**

The water guard is `if 'm3' in str(units): continue` — **written against SI only.** In IP output the
water rows arrive as **`gal`** and **`gal/min`**, pass the guard, fall into the
`else: val_kwh = val` branch, and **are summed into the energy total as kilowatt-hours.** In the
`SingleD` probe that is **20 503.49 gal ≈ 38.6 % of the "corrected" total.**

**The two defects are complementary — every run has exactly one:**

| | SI output | IP output |
|---|---|---|
| demand copy | `W` → **defect 1 fires, large** | `kBtuh` → invisible |
| water rows | `m3` → caught by the guard | `gal` → **defect 2 fires, large** |
| rows affected | `HighRise`, `MidRise`, **all 4 office** | `SingleD`, `OtherDwelling` |

⇒ **`V4-B2_defect_reach.md` §1's claim that all 8 published rows are contaminated is CONFIRMED, and
its explanation of *how* covers only half of them.**

### 🔴 This does not rescue P1

P1 was written against **one** named correction, scored against that correction, and failed. A second
defect found *while investigating the failure* is a new finding, not a re-scoring. The both-defects
numbers live in a **separately labelled post-hoc** artefact (`b2_resid_two_defects.py`, flagged
`"post_hoc": true`), and **P1 stays FALSIFIED in every place it is reported.**

**A prediction does not become correct because the world turned out to be more complicated than it
was.**

### The both-defects measurement — 🟢 landed, same day

Second pass over the **same 400 runs**, storing the full `(ReportName, Units)` decomposition rather
than a pre-summed total, so every variant below is arithmetic on a stored record and no run was
fetched twice. Generator `b2_resid_two_defects.py`, result `v4_b2_resid_two_defects.json`.
**`"post_hoc": true` is written into the result file itself.**

**The unit inventory is printed before any total is read, and both structural assumptions are
checked rather than asserted:**

| `ReportName` | unit | runs | class |
|---|---|--:|---|
| `AnnualBuildingUtilityPerformanceSummary` | `GJ` / `kBtu` | 200 / 200 | energy |
| `AnnualBuildingUtilityPerformanceSummary` | `m3` / `gal` | 200 / 200 | volume |
| `DemandEndUseComponentsSummary` | `W` / `kBtuh` | 200 / 200 | **power — not energy** |
| `DemandEndUseComponentsSummary` | `m3/s` / `gal/min` | 200 / 200 | flow |

✅ **Every unit classified — no total rests on an unknown unit.**
✅ **No power unit appears under the annual report** ⇒ pinning `ReportName` does remove every watt.
✅ **No energy unit appears outside the annual report** ⇒ pinning it discards no real energy.

Those last two lines matter: **an unknown unit silently assumed harmless is how both defects
happened**, and the first run of this script correctly refused to vouch for its own output until `W`
and `kBtuh` were classified by hand.

| row | published | shipped | defect 1 only | **both defects** | 95 % interval | band | movement |
|---|--:|--:|--:|--:|---|---|---|
| `HighRise` | 143.0 IN | 145.46 | 101.23 | **101.23 BELOW** | 99.38 – 104.77 | [113.9, 147.2] | 🔴 **MOVES** |
| `MidRise` | 177.5 IN | 178.38 | 128.21 | **128.21 IN** | 125.05 – 131.18 | [111.1, 216.7] | same |
| `OtherDwelling` | 140.0 IN | 140.12 | 139.88 | **124.98 BELOW** | 121.56 – 130.42 | [136.1, 186.1] | 🔴 **MOVES** |
| `SingleD` | 211.7 **ABOVE** | 211.10 | 210.86 | **130.57 BELOW** | 126.60 – 134.86 | [130.6, 186.1] | 🔴🔴 **INVERTS** |

**How much of each published row is water volume added as energy:**

| row | water share of the defect-1-corrected total |
|---|--:|
| `SingleD` | **38.08 %** |
| `OtherDwelling` | **10.66 %** |
| `MidRise` | 0.00 % |
| `HighRise` | 0.00 % |

**Over a third of the published `SingleD` EUI is gallons of water counted as kilowatt-hours.**

### ⚠️ `SingleD` is BELOW by 0.03 kWh/m², and that is not a verdict

**130.57 against a floor of 130.6.** The point estimate is below by **0.03**, and the interval
**126.60 – 134.86 straddles the floor** — `BELOW` at the bottom, `IN` at the top. 🔴 **The corrected
`SingleD` verdict is genuinely undetermined between BELOW and IN at n = 100.** It is reported as
undetermined and **must not be quoted as "BELOW"** on the strength of a 0.03 margin inside a 8.3-wide
interval.

**What IS determined for `SingleD`: it is no longer ABOVE.** The interval's upper end, 134.86, is far
under the 186.1 ceiling. 🔴🔴 **Leg-2's sole published EUI WARN — `G2r`, raised because `SingleD`
overshoots the SHEU ceiling — does not survive correction. The row lands at the opposite end of the
band, and the WARN as published describes a condition that is not there.** Same inversion shape as
`S9-EUI-hotel`, and for the same reason: a number moved a long way and the finding attached to it did
not move with it.

### 🔴 §3's direction turned out right for `OtherDwelling`. P1 still failed.

These are two different statements and both are true.

- `V4-B2_defect_reach.md` §3 predicted `OtherDwelling` ends up **BELOW**. **Fully corrected, it is
  BELOW — 124.98, whole interval below the floor.** The *direction* was right.
- **P1 was not a direction. P1 was a scored, pre-registered prediction about the correction that was
  defined when it was written** — pin `ReportName` — and against that correction `OtherDwelling` gives
  **139.88, IN**. **P1 failed and stays failed.**

🔴 **A prediction is not retroactively confirmed by a mechanism discovered while investigating its
failure.** §3 was right about where the row lands and wrong about why, by a factor it had no access
to; P1 was the falsifiable form of that claim and it was falsified. **Recording only the first would
be gate-shopping on a prediction instead of a threshold.**

⚠️ And §3's arithmetic is still wrong even where its direction is right: it reached BELOW by dividing
by 1.4868–1.7601. `OtherDwelling`'s actual defect-1 factor is **1.002**; it lands below the floor
because **10.66 % of it is water**, not because of anything §3 modelled.

---

## 6. What did not change

- **Nothing in `Leg2_2-split/` was written to.** No published file edited, no manuscript text touched.
- **The erratum-versus-re-publication choice is still the user's.** This document supplies magnitude.
- **No Leg-3 number is affected.** `3rdJ_08E_aggregate_4split.py:554` builds EUI from the hourly
  `Electricity:Facility` / `NaturalGas:Facility` meters in Joules, never from
  `TabularDataWithStrings`. A meter series carries neither a water row nor a peak-demand duplicate, so
  **neither defect has a surface to act on.** Previously asserted; now verified against the code path.

## 7. Reopen trigger

**Reopens if** `SingleD` is resampled at larger n and its interval clears the 130.6 floor in either
direction. It currently misses by **0.03 kWh/m²** inside an interval **8.3 wide** — the verdict is
undetermined, and **n = 100 is the reason, not the data.** A resample is the only thing that settles
it. 🔴 **Until then `SingleD` corrected is "no longer ABOVE, BELOW-or-IN undetermined", and no
document may shorten that to "BELOW".**

**Reopens if** any run is found whose `(ReportName, Units)` inventory contains a unit classified as
neither energy, volume, nor power. `b2_resid_two_defects.py` prints the full inventory **before** any
total and refuses to vouch for a corrected number while an unclassified unit exists — it did exactly
that on its first run, over `W` and `kBtuh`. **An unknown unit is what caused both defects, and it
will not be assumed away a third time.**

**Reopens if** a sample is found writing a power unit under `AnnualBuildingUtilityPerformanceSummary`,
or an energy unit outside it. Both are checked and both are currently false; if either becomes true,
**pinning `ReportName` stops being a sufficient correction for defect 1** and every number in this
document needs re-reading.

**Not a reopen trigger:** P1's failure. It failed, it is recorded as failed in §3, and the fact that
`OtherDwelling` reaches `V4-B2_defect_reach.md` §3's predicted *direction* by a different mechanism
does **not** reopen or amend the score.

**Not a reopen trigger:** the fact that P1 failed. It failed, it is recorded as failed, and the
document that made it is corrected additively rather than rewritten.
