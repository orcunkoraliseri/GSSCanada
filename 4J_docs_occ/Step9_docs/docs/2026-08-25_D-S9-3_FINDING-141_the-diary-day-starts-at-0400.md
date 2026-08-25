# `D-S9-3` — 🔴 `FINDING 141`: the diary day starts at 04:00, and Step 8's schedules were written as if it started at midnight

#### 4J HETUS LLM pipeline. Written 2026-08-25 (night), from Step 9 item 9.4.
#### This finding is about **Step 8's shipped results**, not about Step 9. Step 9 is already corrected.

---

## 1. The finding, in one paragraph

`D-S2-5` harmonised every diary in this corpus onto a **04:00 day origin**. Minute 0 of every
decoded record is therefore **04:00**, not midnight. `tools/4thJ_step7_schedules.py` writes those
minutes straight into a `Schedule:File`, and **EnergyPlus reads a `Schedule:File` from hour 0 of the
run period, which is midnight.** Every occupancy schedule Step 8 simulated is therefore rotated
**four hours early**: what the model applied at 00:00 is what the diaries recorded at 04:00.

🔴 **This affects all 13,108 EnergyPlus runs Step 8 reported**, including the `f`-sweep behind
`FINDING 133`, the diurnal readings in `FINDING 135`, and the chaining campaign behind `FINDING 136`.

---

## 2. How it was found, and how it was confirmed

It was not found by reading. Step 9's own diurnal aggregate put the **UK domestic hot-water peak at
03:00** and the Spanish electricity peak at 10:00 — neither of which is a residential pattern. The
question that followed was *what does index 0 of this series actually mean?*

**Three independent confirmations, each on a different artefact.**

### (a) The ruling says so

`Step2_docs/4thJ_02_harmonisation.md`, 2026-08-15:

> ✅ **D-S2-1 closes as D-S2-5: the day origin is 04:00, reached by treating each diary as a cyclic
> 24-hour day.** Measured: Spain **06:00**, Italy **04:00**, UK **04:00**.

and `tools/4thJ_gates_step2.py`:

```python
NATIVE_ORIGIN_HOUR = {"es": 6, "uk": 4, "it": 4}
TARGET_ORIGIN_HOUR = 4
def rotation_offset(country):
    """D-S2-14's formula, verbatim: offset = (reference_minutes - 240) mod 1440."""
```

### (b) The generated diaries say so

Sleep (`ACL 011`) as a share of respondents, by **minute-index hour**, 1,500 diaries per fold:

| index | 0 | 1 | 2 | 3 | 4 | … | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **es** | 1.00 | 1.00 | 0.98 | **0.27** | 0.18 | … | 0.23 | 0.45 | 0.61 | 0.78 | 0.82 | 0.69 |
| **uk** | 1.00 | 0.99 | 0.96 | **0.61** | 0.53 | … | 0.09 | 0.30 | 0.66 | 0.84 | 0.91 | 0.82 |
| **it** | 0.98 | 0.93 | 0.86 | **0.57** | 0.53 | … | 0.14 | 0.33 | 0.52 | 0.64 | 0.75 | 0.66 |

People wake between index 3 and index 5 and fall asleep from index 18. On a **04:00 origin** that is
waking at **07:00–09:00** and falling asleep from **22:00** — correct. On a midnight origin it would
be waking at 03:00 and asleep at 22:00, which no population does.

### (c) The SHIPPED Step 8 schedules say so

Mean presence over the 100 shipped `presence_HH_*.csv` files, by schedule hour index:

| fold | trough at index | presence at trough | peak at index |
|---|---|---|---|
| es | 7 | 0.37 | 0 (0.995) |
| uk | 7 | 0.23 | 0 (0.99) |
| it | 7 | 0.39 | 0 (0.99) |

Read on a **04:00 origin**, the trough is **11:00–13:00** and the peak is **04:00** — a residential
day. Read on a midnight origin, the trough is 07:00 and presence would *rise* through the afternoon
and *fall* through the evening, which is the pattern inverted.

🔴 **All three artefacts agree, and they are not derived from one another**: a ruling document, the
generated corpus, and the schedules on disk.

---

## 3. What it is NOT

* **It is not a cross-fold confound.** All three countries were rotated to the same 04:00 origin by
  `D-S2-5`, so the error is identical in every fold. No LOCO comparison is biased *between* folds by
  it. This is the opposite of `FINDING 120` and `FINDING 131`, whose sign differed by fold.
* **It does not affect any quantity that has no time-of-day.** Annual totals, the between-diary
  spread, `FINDING 134`'s annual finding, and the mapping work of items 9.1-9.3 are untouched.
* **It is not `FINDING 131`.** That was the day-of-WEEK alignment — a Friday-start diary year wired
  into a Sunday-start `RunPeriod`. This is the hour-of-DAY alignment. They are the same family and
  neither was checked before the other was found. `FINDING 99` anticipated the family.

---

## 4. What it IS, and what is at risk

The occupancy signal is a **peak** signal — that is `FINDING 133`, the step's headline. A peak
result is a statement about **when**, and a four-hour rotation is a change to exactly that.

| Step 8 reading | at risk? | why |
|---|---|---|
| `FINDING 133` annual channel (+1.82 / −0.04 / +0.06 %) | 🟢 **no** | an annual total does not depend on when the gain lands |
| `FINDING 133` **peak** channel (+6.38 / +4.54 / +3.96 %) | 🔴 **yes** | coincident peak depends on when occupancy overlaps the weather and the thermostat |
| `FINDING 134` (effect smaller than spread on annual) | 🟢 **no** | annual |
| `FINDING 135` diurnal profile (`uk` 5 → 7, `it` 6 → 7 at `f ≥ 0.50`) | 🔴 **yes** | these hour labels are four hours early; read as **09:00 → 11:00** and **10:00 → 11:00** |
| `FINDING 135` "the annual peak hour never moves — 7 in every fold" | 🟡 **partly** | 7 is the thermostat recovery hour, which is set in the IDF and is NOT rotated; the reading stands, but "7" is a genuine 07:00 while the occupancy beside it is not |
| `FINDING 136` / decision 14's null (0.178 / 0.075 / 0.239 % on peak) | 🟡 **probably not** | the null says the chaining axis moves peak far less than sampling noise. A rotation applied identically to every rule point cannot create a difference between rule points. The **magnitude** could move; the **comparison** should not |
| `FINDING 121`-`125`, the four unruled conventions, the envelope work | 🟢 **no** | none of them is time-of-day resolved |

---

## 5. What Step 9 already did about it

🟢 **Step 9 is corrected and the correction is declared, not silent.**

`tools/4thJ_step9_trigger.py` carries `DIARY_ORIGIN_HOUR = 4` with the measurement above beside it,
and `rotate_to_midnight()` applies **one cyclic shift of the whole year series** before emission.

🔴 **The rotation is cyclic over the YEAR, not within each day**, and that distinction is the whole
correctness of it: a diary day runs 04:00 of day *D* to 04:00 of day *D+1*, so its last four hours
belong to the **next** calendar day. Rotating each day inside itself would move those four hours
*backwards by twenty hours* instead of forwards by four.

Every Step 9 manifest carries `"rotated_to_midnight": true` and `"diary_origin_hour": 4`, so an
unrotated run can never be mistaken for a rotated one.

**Measured effect on Step 9's own output** (fold `es`, mean W per dwelling by clock hour):

| | trough | midday peak | evening plateau |
|---|---|---|---|
| **rotated (shipped)** | **05:00**, 86 W | **14:00**, 503 W | 19:00-22:00, 436 / 360 / 375 / 321 W |
| unrotated (what Step 8's convention would give) | 01:00 | 10:00 | 15:00-18:00 |

The rotated profile is a Spanish domestic load curve — minimum before dawn, a lunch peak, an evening
plateau. The unrotated one is not.

---

## 6. 🔴 The decision, and why it is the author's

**Step 9 cannot be shipped alongside Step 8 as things stand**, because the two would disagree about
what time it is inside the same building: appliance and hot-water gains at the correct hour,
occupancy gains four hours early.

### The options

* **(a) Re-emit Step 7's schedules with the rotation and re-run Step 8.**
  The fix in `4thJ_step7_schedules.py` is one cyclic shift, the same function Step 9 now uses. The
  cost is the campaign: **13,108 EnergyPlus runs, about 1,530 s + 659 s + the 8.3 and 8.4 probes**,
  all local, no GPU and no Speed job. Every Step 8 gate would need re-scoring and `FINDING 133`'s
  peak magnitudes and `FINDING 135`'s hour labels would need re-deriving.
  🟢 **This is the recommendation.** The correction is cheap, the defect is real, and the peak claim
  is the paper's headline.

* **(b) Leave Step 8 as it is, and rotate Step 9 to match it.**
  Internally consistent, and wrong in both steps. It would require the manuscript to state that all
  reported occupancy is four hours early, which is not a limitation a reviewer would accept for a
  claim about peak timing.

* **(c) Leave Step 8 as it is, publish the annual results only, and withdraw the peak claim.**
  `FINDING 134` already forbids the annual claim. (c) therefore leaves the paper with no occupancy
  claim at all, which is worse than (a) by a wide margin.

* **(d) Re-run only the cells the peak claim rests on.**
  Possible, but the gate board is scored over the whole campaign and a partially re-run campaign has
  two conventions in it. `FINDING 130` is the precedent for how that ends.

### Recommendation

🟢 **(a).** It is the only option that leaves a defensible peak claim, and its cost is measured in
minutes of local EnergyPlus, not in a queue.

🔴 **Whatever is ruled, the four-hour offset must appear in the methods.** It was in the pipeline
from Step 2's ruling to Step 8's campaign without a single document naming it, and that is worth one
sentence in the limitations regardless of which way the re-run goes.

---

## 7. What this says about the gate set, which is the durable part

No Step 7 or Step 8 gate could have caught this. They check that a schedule has **8,760 values**,
that `Interpolate to Timestep` is `No`, that `Minutes per Item` matches the timestep, that the
values are in `[0, 1]`, that the multiplier rebuilt from the diary matches the series the saved
`in.idf` points at, and that the diary is located by content in the right fold's bundle. **Every one
of those is true of a series rotated by four hours.**

🔴 The missing check is a **phase** check, and it is cheap: assert that the emitted schedule's daily
minimum falls in the small hours and its maximum does not. A residential presence schedule whose
trough sits at 07:00 is wrong however well-formed it is.

Proposed as `G7.19` / `G8.17` — **additive, no existing band touched** — to be written only if the
author rules (a) or (b), since under (c) the schedules would not ship at all.

---

## Author's ruling

🟢 **RULED 2026-08-26 (early) BY THE AUTHOR: OPTION (a) — RE-EMIT STEP 7's SCHEDULES WITH THE
ROTATION AND RE-RUN THE STEP 8 CAMPAIGN.** Instruction given as *continuer jusqu'a la fin* on the
report that carried this recommendation.

### What (a) obliges, and what was done

| obligation | state |
|---|---|
| the rotation lands in `tools/4thJ_step7_schedules.py`, declared and stamped | 🟢 done — `rotate_to_midnight()`, `DIARY_ORIGIN_HOUR = 4`, `"rotated_to_midnight": true` in every manifest |
| a **phase gate**, since §7 showed no existing gate could see this | 🟢 done — **`G7.19`** on the emitted schedule and **`G8.17`** on the campaign that consumes it, both additive, no existing band touched |
| the phase gate is **seen failing** | 🟢 done — the emitter carries a `--no-rotate` PERTURBATION-ONLY switch, so the falsifier is an artefact anyone can rebuild, not a one-off |
| Step 7's bundles re-emitted | 🟢 done |
| the Step 8 campaign re-run in full | 🟢 done |
| every Step 8 gate re-scored on the re-run | 🟢 done |
| `FINDING 133`'s peak magnitudes and `FINDING 135`'s hour labels re-derived | 🟢 done — see `FINDING 143`-`FINDING 146` in the Step 8 record |
| the four-hour offset named in the methods regardless of the ruling | 🟢 owed to the manuscript, carried on the Step 8 document |

🔴 **The ruling does not retire `FINDING 141`.** The finding is that a defect crossed Steps 2, 7
and 8 without a single document naming it, and that stands whatever the re-run returns. What the
re-run decides is only whether the reported numbers are the rotated ones.

