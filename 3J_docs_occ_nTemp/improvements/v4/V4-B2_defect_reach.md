# V4-B2 — how far the `calculate_eui()` defect reaches into Leg-2's published numbers

**2026-08-06 · read-only on `Leg2_2-split/` · no simulation, cluster not contacted.**
Generator: `improvements/v4/b2_eui_defect_reach.py` · data: `v4_b2_defect_reach.json`.
**Decision this serves:** §4.3 — *quantify from local outputs before choosing between an erratum and a
re-publication.* **It does not choose. It reports what the local artefacts can and cannot settle.**

---

## 0. The three results, up front

1. 🔴 **The defect is not office-only. It reaches every EUI number Leg-2 published** — the four
   residential rows as well as the four office rows.
2. 🔴🔴 **The factor is NOT uniform. Measured across 12 real Leg-2 cells it runs 1.4868 – 1.7601, an
   18.4 % spread.** The pre-registration said *"the factor is uniform" is a claim to be shown, not
   assumed*. **It was shown false.** `172.7 ÷ 1.706` is not a valid correction.
3. 🔴 **At least two published in-band results become out-of-band under the entire measured range**,
   and four more flip or not depending on a factor that **cannot be measured on this machine.**

**The reach question is answered. The corrected numbers are BLOCKED, and reported as blocked** (§4).

---

## 1. The defect, confirmed in the shipped code

`Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py`, inside `calculate_eui()`:

```python
query = """
SELECT TableName, RowName, ColumnName, Units, Value
FROM TabularDataWithStrings
WHERE TableName = ? OR TableName = ?
"""
df = pd.read_sql_query(query, conn, params=('End Uses By Subcategory', 'End Uses'))
```

**`ReportName` is never filtered**, and EnergyPlus emits a table of that name under **both**
`AnnualBuildingUtilityPerformanceSummary` (**GJ**) and `DemandEndUseComponentsSummary` (**W**). The
unit guard drops only `m3`, and the conversion chain ends:

```python
else:
    # Unknown unit - skip or assume kWh
    val_kwh = val
```

**`W` is an unknown unit, so every watt row is added as a kilowatt-hour.** The comment says *skip or
assume kWh*; the code does not skip.

### The reach is the call site, and it is not channel-specific

`Step8_docs/3rdJ_08_simulation_2split_agg.py` calls `_eui_from_sql()` → `calculate_eui()` in **two**
places: line **438** on the **residential** branch and line **481** on the **office** branch. Both
write the same `eui_kWh_m2` column, and `Step9_docs/3rdJ_09_activityDrivenLoads_2split.py`
`build_eui()` takes the **median of that column** for the residential archetypes *and* for office.

⇒ **All eight rows of `Step9_docs/outputs_step9/step9_eui_by_channel.csv` are contaminated**, not the
four office rows the finding was originally written about.

---

## 2. The measurement — 12 local Leg-2 cells

Every `eplusout.sql` that exists under `Leg2_2-split/` on this machine: 4 distinct cells
(HighRise / MidRise × two households, Winnipeg 7A, 2022) across 3 campaign arms.

| cell | area m² | shipped EUI | corrected EUI | **factor** |
|---|--:|--:|--:|--:|
| `campaign_smoke` HighRise s001 | 7059.9 | 162.21 | 92.53 | **1.7529** |
| `campaign_smoke` HighRise s002 | 7059.9 | 177.00 | 109.85 | **1.6114** |
| `campaign_smoke` MidRise s001 | 2824.0 | 219.48 | 147.62 | **1.4868** |
| `campaign_smoke` MidRise s002 | 2824.0 | 211.96 | 138.45 | **1.5309** |
| `campaign_smoke_v2` HighRise s001 | 7059.9 | 161.75 | 92.08 | **1.7566** |
| `campaign_smoke_v2` HighRise s002 | 7059.9 | 175.83 | 108.69 | **1.6177** |
| `campaign_smoke_v2` MidRise s001 | 2824.0 | 216.94 | 144.61 | **1.5002** |
| `campaign_smoke_v2` MidRise s002 | 2824.0 | 209.78 | 136.57 | **1.5360** |
| `campaign_smoke_v2_1b` HighRise s001 | 7059.9 | 161.33 | 91.66 | **1.7601** |
| `campaign_smoke_v2_1b` HighRise s002 | 7059.9 | 174.28 | 107.14 | **1.6267** |
| `campaign_smoke_v2_1b` MidRise s001 | 2824.0 | 213.99 | 142.20 | **1.5049** |
| `campaign_smoke_v2_1b` MidRise s002 | 2824.0 | 208.90 | 135.43 | **1.5425** |

**min 1.4868 · max 1.7601 · spread 18.38 % of the minimum.**

🔴 **The factor tracks the *household*, not the arm.** HighRise s001 sits at 1.75–1.76 in all three
arms; MidRise s001 at 1.49–1.50 in all three. **The contamination is the ratio of the building's peak
demand to its annual energy — a per-building, per-schedule quantity.** That is exactly why it cannot be
divided out with a constant, and why **a factor measured on residential cells says nothing reliable
about the office tower.**

### 🔴 CORRECTION, same day — **every cell in this table is from the contaminated half of the sample**

> Added 2026-08-06 after the 400-run residential retrieval. **The table above is not wrong; it is
> unrepresentative, and it could not have known that.** Every one of the 12 local SQL files is
> `HighRise` or `MidRise`. Measured over 100 runs per archetype from the actual published campaign:
>
> | archetype | factor over 100 published runs |
> |---|---|
> | `HighRise` | 1.2038 – 1.7541 |
> | `MidRise` | 1.1785 – 1.7400 |
> | `SingleD` | **1.0005 – 1.0026 — all 100 runs** |
> | `OtherDwelling` | **1.0007 – 1.0024 — all 100 runs** |
>
> **The residential factor is not an 18.4 % spread. It is 75.3 %, and it separates cleanly by
> archetype** — two of the four residential rows are essentially uncontaminated by this defect.
> (**Not** "bimodal" — the separation has a named mechanism, stated next, and naming the shape instead
> of the cause is the error `V4-A5` was written to correct.)
>
> **The mechanism is the unit system.** `SingleD`/`OtherDwelling` runs report in **IP** (`kBtu`,
> `kBtuh`, `gal`); `HighRise`/`MidRise` in **SI** (`GJ`, `W`, `m3`). §1's defect inflates a sum through
> the `W` rows, and `W` only appears in SI output — in IP the demand copy arrives as `kBtuh`, roughly a
> thousandth of the annual `kBtu`, so it disappears into rounding.
>
> ⚠️ **This does not make the IP rows sound.** It makes them wrong *for a different reason* — see the
> second defect, §8. A factor of 1.00 here means "§1's defect did not fire", not "the number is right".
>
> **What generalises:** §2's real finding — *the factor is a per-building quantity and cannot be
> divided out* — survives and is strengthened. What does not generalise is its **range**, which was
> measured on 12 files that all happened to sit on one side of a split nobody knew was there.

---

## 3. What this does to the eight published rows

Bracketed by the **mildest** and **strongest** measured factors. ⚠️ **These are brackets, not
corrections** — see §4.

| published row | published | ÷1.4868 | ÷1.7601 | band | published verdict | corrected verdict |
|---|--:|--:|--:|---|---|---|
| office all | 172.7 | 116.16 | 98.12 | [100, 200] | IN | **depends on the factor** |
| office Knowledge | 172.6 | 116.09 | 98.06 | [100, 200] | IN | **depends on the factor** |
| office Public | 172.5 | 116.02 | 98.01 | [100, 200] | IN | **depends on the factor** |
| office Sales | 172.7 | 116.16 | 98.12 | [100, 200] | IN | **depends on the factor** |
| resid SingleD | 211.7 | 142.39 | 120.28 | [130.6, 186.1] | **ABOVE** (the sole WARN) | **depends** — IN, or BELOW |
| resid OtherDwelling | 140.0 | 94.16 | 79.54 | [136.1, 186.1] | IN | 🔴 **BELOW, either way** |
| resid MidRise | 177.5 | 119.38 | 100.85 | [111.1, 216.7] | IN | **depends on the factor** |
| resid HighRise | 143.0 | 96.18 | 81.25 | [113.9, 147.2] | IN | 🔴 **BELOW, either way** |

**Two published PASSes fall out of band across the whole measured range** — `OtherDwelling` and
`HighRise` clear their floors by no factor in [1.4868, 1.7601].

🔴 **And the sole published WARN can move in either direction.** `G2r` WARNs because SingleD 211.7 is
**above** the SHEU ceiling. Corrected it is either **inside the band** (WARN → PASS) or **below the
floor** — out of band at the *opposite end*, same verdict, opposite meaning. **The same inversion shape
as `S9-EUI-hotel`**, and for the same underlying reason: a number moved a long way and the count that
described it did not.

**So yes — a published conclusion moves, not merely a digit.** That was the question §4.3 asked, and it
is now answered without needing the exact numbers.

### 🔴 CORRECTION, same day — **the "BELOW, either way" cells were pre-registered and one of them FAILED**

> Added 2026-08-06. The two 🔴 cells above were the strongest claims in this document — the only two
> called out as holding across the *entire* measured range. They were turned into a written prediction
> (`V4-B2_PREREGISTRATION_resid_sample.md`, **P1**) before a single residential campaign file was
> fetched, and then scored on 100 runs per archetype:
>
> | published row | §3 said | measured (§1 defect corrected) | 95 % interval | **P1** |
> |---|---|--:|---|---|
> | resid `HighRise` | 🔴 BELOW, either way | **101.23** — BELOW | 99.38 – 104.77 | ✅ confirmed |
> | resid `OtherDwelling` | 🔴 BELOW, either way | **139.88** — **IN** | 135.47 – 145.48 ⚠️ straddles the 136.1 floor | 🔴 **FALSIFIED** |
> | resid `MidRise` | depends | 128.21 — IN | 125.05 – 131.18 | *(not predicted)* |
> | resid `SingleD` | depends — IN, or BELOW | **210.86** — **ABOVE**, unmoved | 207.15 – 217.11 | P2, no direction predicted |
>
> **The `OtherDwelling` row above is WITHDRAWN, not softened.** And the `SingleD` reading is withdrawn
> with it: §3 offered *"IN, or BELOW"* and the measured answer is **neither** — it does not move at all,
> because the ÷1.4868–1.7601 bracket applied to it a factor its own runs never had (**1.003**).
>
> **Why it failed is the whole point.** §3's brackets are the §2 factors, and §2's factors came from 12
> SI files. `OtherDwelling` and `SingleD` are IP. Applying a measured-elsewhere factor to a row is the
> exact operation §2 itself warned against for office — **the warning was right and this document
> broke it two sections later.** The office row was protected by an explicit caveat; the residential
> rows were not, because they looked like same-channel neighbours. **Same channel was not the axis that
> mattered. The unit system was, and nothing here knew it existed.**
>
> ⚠️ Two of the four residential rows above are **still not corrected** — `SingleD` and
> `OtherDwelling` carry a *second* defect that this correction does not remove (§8). Their measured
> values in the table above are "§1 corrected", which for an IP run is very nearly the shipped value.

---

## 4. ~~🔴 What is BLOCKED, and it is reported as blocked~~ — 🟢 **UNBLOCKED the same day, 2026-08-06**

> 🟢 **§4 below is superseded and kept intact.** Its reasoning was sound; its **premise was a rule that
> the user changed hours later**: *"tu peux obtenir ce que choses tu veux sur le speed, mais tu ne peux
> pas utiliser pour des simulations."* **Retrieval is permitted; running anything on the cluster is
> not.** The campaign SQL was therefore not blocked at all — it was a file that had to be fetched.
>
> **"Blocked because the file is on Speed" stopped being a valid status**, and this item is the one it
> was written on. All 252 published office runs were copied off Speed one at a time with `scp`, read
> locally with `sqlite3`, and deleted before the next — peak local disk one file, **no `sbatch`, no
> `srun`, no `python` on the login node, no simulation.**
>
> **Corrected numbers: `V4-B2_corrected.md`** (office, all 252 runs, measured) and
> `V4-B2_PREREGISTRATION_resid_sample.md` (residential, a pre-registered sample — 8,400 runs is a
> bandwidth limit, and it is reported as a sample with an interval rather than extrapolated).
>
> ⚠️ **What did NOT change: §3's brackets are still not corrections**, and §2's residential factors
> still say nothing about an office building. The office half is now measured rather than bracketed,
> which is why it needed its own document.

## ~~4. What is BLOCKED, and it is reported as blocked~~ *(superseded — see above)*

**The corrected values for the published cells cannot be computed on this machine.**

- `Leg2_2-split/Step8_docs/outputs_step8/office/` is **empty**; `office_idfs_v242/` holds **4 `.idf`
  files and no results**. **There is no Leg-2 office SQL anywhere on this machine.**
- The 12 SQL that do exist are **residential smoke cells**, not the campaign cells behind the published
  medians (office n = 252, residential n = 2100 per archetype).
- Recomputing requires the campaign `eplusout.sql` set, which is on **Speed**. **The standing rule is
  stay local — Speed is not contacted at all.** This is not a downgrade to the cheapest option; it is
  the pre-registered outcome of §4.3's guard firing.

⚠️ **Do not treat §3's brackets as the corrected numbers.** For the residential rows they are a
same-channel, different-sample extrapolation. **For the four office rows they are not even that** — the
factor depends on a building's demand-to-energy ratio, and no office building was measured. The office
row is bracketed only to show that **the 100 floor lies inside the plausible range**, which is what
makes the disclosure question live.

---

## 5. One thing that got harder to explain, not easier

The three office subtype medians are **172.6 / 172.5 / 172.7 — a spread of 0.2 kWh/m², 0.12 %** across
three different occupancy profiles. That tightness was already on record as circumstantial support for
the defect.

**It is now more puzzling, not less.** The contamination term varies by **18 %** between two
residential households in the same archetype and city. If the same term is inside all three office
subtype medians, something is compressing them. **Two candidates, neither tested here:** the office
subtypes may genuinely differ very little in total energy, or the demand-driven term may dominate the
sum and swamp the schedule differences. **Distinguishing them needs the office SQL. Recorded as an open
question, not as evidence for either reading.**

---

## 6. What did not change

**Nothing in `Leg2_2-split/` was written to.** No Leg-2 number was corrected, no manuscript text was
touched, and **the erratum-versus-re-publication choice is not taken here** — §4.3 reserved it for the
user, with the magnitude in hand. What is now in hand is: **the reach (all 8 rows), the mechanism (a
per-building demand ratio), the refutation of uniformity (18.4 %), and the fact that at least two
published in-band results do not survive correction.**

## 7. Reopen trigger — ✅ **fired 2026-08-06, hours after it was written**

~~**This item is BLOCKED on the campaign SQL, not finished.** It reopens the moment Leg-2's Step-8
outputs are available to a local process — at which point `b2_eui_defect_reach.py` runs unchanged over
the campaign cells and produces the per-cell factors.~~ 🔴 **Until the corrected value for a row is
measured, no Leg-2 EUI figure may be quoted as corrected, and none may be quoted as sound either.** The
published values are known to be wrong; the right ones are known **only where they have been measured**
— which is now the four office rows, and a sample of the four residential ones.

🟢 **Fired.** The trigger said *"the moment Leg-2's Step-8 outputs are available to a local process"* —
and what made them available was **a rule change, not a transfer that had failed.** Worth keeping in
view: this item spent a day reported as blocked on compute when it was blocked on nothing but a reading
of the standing instruction. **When something is blocked, name the resource — and check whether the
block is the resource or the rule.**

---

## 8. 🔴🔴 A SECOND defect in the same function — added 2026-08-06

This document was written about one defect. Chasing why **P1** failed found another, in the same
function, **independent of the first**, and it is the reason two published rows still cannot be
called corrected.

### The code

`Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py`, `calculate_eui()`:

```python
if 'm3' in str(units):          # line 319 — the water guard
    continue
...
else:
    # Unknown unit - skip or assume kWh
    val_kwh = val               # line 344 — everything else becomes kWh
```

**The water guard is SI-only.** It is written against `m3` and `m3/s`. When EnergyPlus writes the same
building in **IP** units, the water rows arrive as **`gal`** and **`gal/min`** — which sail past the
guard, fall into the `else`, and are **summed into the energy total as kilowatt-hours.**

### Confirmed on two probe files, one of each unit system

| | `SingleD` probe | `HighRise` probe |
|---|---|---|
| annual energy | **111 081.75 kBtu** | **2 553.25 GJ** |
| peak demand | **47.95 kBtuh** | **223 043.11 W** |
| water | **20 503.49 gal** | **963.66 m3** |
| unit system | **IP** | **SI** |
| defect 1 (`W` summed as kWh) | negligible — `kBtuh` ≈ kBtu/1000 | **large** |
| defect 2 (water summed as kWh) | **large — 38.6 % of the total** | none — `m3` is caught |
| reproduces the run's factor | 1.000905 ✅ | 1.314483 ✅ |

Both factors are reproduced by arithmetic on the stored rows, so the mechanism is not inferred from
the shape of a distribution — it is the arithmetic.

### 🔴 The two defects are complementary. Every run has exactly one of them.

- **SI output** → demand is `W`, water is `m3`. **Defect 1 fires, defect 2 cannot.**
- **IP output** → demand is `kBtuh`, water is `gal`. **Defect 2 fires, defect 1 cannot.**

⇒ **§1's statement that all 8 published rows are contaminated is confirmed, and its explanation of how
covers only half of them.** No published row escapes; the four office rows and the two SI residential
rows are hit by defect 1, the two IP residential rows by defect 2.

### What this does NOT do

🔴 **It does not rescue P1.** P1 was written against one named correction, scored against that
correction, and failed. A second defect discovered *while investigating the failure* is a new finding,
not a re-scoring, and it is labelled post-hoc in `b2_resid_two_defects.py` and everywhere it is
reported. **A prediction that fails does not become a prediction that succeeded because the world
turned out more complicated than it.**

### Reach, checked rather than assumed

- **Office — unaffected by defect 2.** Every one of the 252 published office runs has a factor ≥ 1.5.
  An IP run cannot: defect 1 is invisible in IP, so an IP run's factor sits at ~1.00. **All 252 office
  runs are therefore SI, their water is `m3`, and the shipped guard drops it correctly.** Inferred from
  data already in hand; no re-retrieval needed, and the inference is stated so it can be attacked.
- **Leg-3 — immune to both.** `Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py:554` builds EUI as
  `energy_J * J_TO_KWH / area_m2` from the **hourly `Electricity:Facility` / `NaturalGas:Facility`
  meters** (`:343`), never from `TabularDataWithStrings`. A meter series carries no water rows and no
  peak-demand duplicate, so neither defect has a surface to act on. **This was previously asserted;
  it is now verified against the code path.**

### 8.1 Measured — what both defects together do to the four residential rows

400 runs (100 per archetype, the pre-registered sample), full `(ReportName, Units)` decomposition
stored rather than a pre-summed total. `b2_resid_two_defects.py` → `v4_b2_resid_two_defects.json`,
which carries `"post_hoc": true`.

| row | published | defect 1 only | **both defects** | 95 % interval | band | movement |
|---|--:|--:|--:|---|---|---|
| `HighRise` | 143.0 IN | 101.23 | **101.23 BELOW** | 99.38 – 104.77 | [113.9, 147.2] | 🔴 **MOVES** |
| `MidRise` | 177.5 IN | 128.21 | **128.21 IN** | 125.05 – 131.18 | [111.1, 216.7] | same |
| `OtherDwelling` | 140.0 IN | 139.88 | **124.98 BELOW** | 121.56 – 130.42 | [136.1, 186.1] | 🔴 **MOVES** |
| `SingleD` | 211.7 **ABOVE** | 210.86 | **130.57** | 126.60 – 134.86 | [130.6, 186.1] | 🔴🔴 **INVERTS** |

**Water counted as energy: 38.08 % of `SingleD`, 10.66 % of `OtherDwelling`, 0.00 % of the SI rows.**

⚠️ **`SingleD` is BELOW by 0.03 kWh/m² inside an interval 8.3 wide — the corrected verdict is
UNDETERMINED between BELOW and IN, and must not be quoted as BELOW.** What *is* determined: **it is no
longer ABOVE**, the whole interval sitting far under the 186.1 ceiling.

⇒ 🔴🔴 **§0's third result is superseded upward. It said "at least two published in-band results become
out-of-band". Measured: THREE of the eight published rows change verdict** — `HighRise` and
`OtherDwelling` fall below their floors, and **Leg-2's sole published EUI WARN inverts.** The four
office rows do not move (`V4-B2_corrected.md` §2), and `MidRise` does not move.

### 8.2 §3's direction was right for `OtherDwelling`. **P1 still failed, and stays failed.**

Both statements are true and they are not the same statement.

§3 predicted `OtherDwelling` ends **BELOW**, and fully corrected it is BELOW with its whole interval
under the floor. But §3 got there by **dividing by 1.4868–1.7601**, and that row's actual defect-1
factor is **1.002**. It lands below the floor because **10.66 % of it is water** — a mechanism §3 had
no access to and did not model. **Right answer, wrong arithmetic, and the arithmetic was the claim.**

**P1 is the falsifiable form of §3**, and it was scored against the correction that was defined when it
was written — pin `ReportName` — giving `OtherDwelling` **139.88, IN**. 🔴 **P1 FAILED. It is not
rescued by a second defect discovered while investigating its failure**, and recording only the
half that came out right would be gate-shopping applied to a prediction instead of a threshold.

**The general rule this earns:** *a correction is only as pre-registered as its definition. Naming the
direction is not enough — the arithmetic that produces it is part of the claim, and a prediction that
reaches the right verdict through the wrong quantity has not been confirmed.*
