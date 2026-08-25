# `D-S9-3`(a) — the rotated re-run: what changed when Step 8's occupancy was put on the right clock

#### 4J HETUS LLM pipeline. Written 2026-08-26 (early), after the author ruled `D-S9-3` (a).
#### 🔴 **This document supersedes `FINDING 133`, `FINDING 134` and `FINDING 135`. Do not quote any of the three from an earlier file.**

---

## 1. What was ruled, and what it obliged

`FINDING 141`: `D-S2-5` harmonised every diary onto a **04:00** day origin,
`tools/4thJ_step7_schedules.py` wrote minute 0 into a `Schedule:File`, and **EnergyPlus reads a
`Schedule:File` from midnight**. Every occupancy schedule Step 8 simulated on 2026-08-25 — all
**13,108 runs** — applied occupancy **four hours early**.

The author ruled **(a): re-emit and re-run**. This document is what the re-run returned.

🔴 **The short version: the peak claim does not survive the rotation, and the annual channel changes
sign.** The correction is not cosmetic and it is not small.

---

## 2. The change, and the evidence that it is ONLY the rotation

`rotate_to_midnight()` in the emitter, one call, **cyclic over the whole year and not within each
day** — a diary day runs 04:00 of day *D* to 04:00 of day *D+1*, so its last four hours belong to the
next calendar day.

| claim | how it was checked | result |
|---|---|---|
| the change is exactly the rotation and nothing else | `--no-rotate` re-emits and is compared to the shipped pre-rotation bundle | **byte-for-byte, 100 of 100 presence files and the `.idf`** |
| the rotation itself is right | compared against `tools/4thJ_step9_trigger.py`'s **independent** implementation, written a day earlier | **0 of 100 × 8,760 values disagree** |
| Step 9 still models Step 8's dwellings | `_assert_same_dwellings` rotates its own rebuild before comparing | **300 of 300 across three folds**, and **seen failing** on the pre-rotation bundle |
| the schedule-free control is untouched | the 8.3 campaign re-run and compared to its own previous output | `control_annual.csv` **identical**, 88 cells, 208.2 s |

🟢 That last row matters more than it looks: it is the null. A campaign with no schedule in it cannot
move when the schedules move, and it did not.

---

## 3. The two new gates, and why they had to exist

§7 of the `D-S9-3` brief established that **no gate in Steps 7 or 8 could see this**. They check 8,760
values, `Interpolate to Timestep = No`, `Minutes per Item`, the range [0, 1], and the multiplier
rebuilt from the artefact on disk. **Every one of those is true of a series rotated by four hours.**

* **`G7.19`** scores the emitter: mean presence at **05:00** is at least **0.90** of the schedule's
  own daily maximum; the daily trough falls at **08:00 or later**; the manifest **declares**
  `rotated_to_midnight`. Both numeric arms are **self-referenced**, so no rescaling can meet them.
* **`G8.17`** scores the consumer, because a corrected emitter does not stop a campaign being pointed
  at an old bundle — and the old bundles are still on disk.

Both are additive. **No existing band was touched and `prereg.md` is unchanged.**

### Both were seen failing, on the real artefact

`G7.19` falls on `outputs_step7/schedules/perturb_norotate/`, which the emitter's own `--no-rotate`
switch rebuilds on demand. `G8.17` falls on injection **`I19`**, which stages the **actual tree the
13,108 runs consumed** (`Step7_docs/outputs_step7/schedules_bak_prerotation/`).

| bundle | mean presence at 05:00 / daily max | trough |
|---|---|---|
| **rotated** `es` / `uk` / `it` | **0.9998 / 0.9979 / 0.9498** | **11:00 / 11:00 / 13:00** |
| pre-rotation `es` / `uk` / `it` | 0.674 / 0.787 / 0.767 | 07:00 / 07:00 / 09:00 |

The registered band, **0.90**, sits inside that gap and was fixed before either side was scored.

---

## 4. 🔴 `FINDING 143` — THE PEAK CLAIM DOES NOT SURVIVE THE ROTATION

`FINDING 133` was the step's headline: the occupancy channel is a **peak** channel. `FINDING 134` then
killed the annual claim because the effect was smaller than the between-diary spread, and let the peak
claim stand because there it was **1.7 to 2.0×** the spread.

**On the rotated campaign the peak effect is smaller than the spread in all three folds.**

| fold | peak %, pre-rotation | its diary spread | ratio | **peak %, ROTATED** | its diary spread | **ratio** |
|---|---|---|---|---|---|---|
| `es` | +6.3841 | 3.7350 | 1.71 | **+2.7145** | 4.9837 | **0.54** |
| `uk` | +4.5380 | 2.5803 | 1.76 | **+0.0393** | 2.3797 | **0.02** |
| `it` | +3.9594 | 1.9566 | 2.02 | **−0.6332** | 1.5959 | **0.40** |

🔴 **In Italy the sign flips.** 🔴 **In Britain the effect is two hundredths of the spread — which is
to say it is not there.**

`FINDING 134`'s test, applied to the channel it had spared, now returns the same verdict. **At the top
of the pre-registered sweep, no occupancy claim survives on either channel.**

---

## 5. 🔴 `FINDING 144` — THE ANNUAL CHANNEL CHANGES SIGN, AT EVERY LEVEL OF `f`, IN EVERY FOLD

The whole grid, re-derived from `agg_by_fold.csv`. The reporting rule
(`archetype_parameter_provenance.md` §9.3) forbids quoting one level, so here are all five.

| fold | `f` | annual % | its spread | ratio | peak % | its spread | ratio |
|---|---|---|---|---|---|---|---|
| `es` | 0.15 | −0.3299 | 0.2689 | 1.23 | +0.2689 | 0.7484 | 0.36 |
| `es` | 0.30 | −0.6217 | 0.5374 | 1.16 | +0.6944 | 1.5195 | 0.46 |
| `es` | 0.50 | −0.9517 | 0.9010 | 1.06 | +1.2861 | 2.4000 | 0.54 |
| `es` | 1.00 | **−1.5100** | 1.8870 | 0.80 | **+2.7145** | 4.9837 | 0.54 |
| `uk` | 0.15 | −0.0843 | 0.0755 | 1.12 | −0.3595 | 0.4306 | 0.83 |
| `uk` | 0.30 | −0.1510 | 0.1293 | 1.17 | −0.4068 | 0.8695 | 0.47 |
| `uk` | 0.50 | −0.2294 | 0.1937 | 1.18 | −0.2283 | 1.3953 | 0.16 |
| `uk` | 1.00 | **−0.3605** | 0.3155 | 1.14 | **+0.0393** | 2.3797 | 0.02 |
| `it` | 0.15 | −0.0697 | 0.0494 | 1.41 | −0.2209 | 0.1572 | 1.41 |
| `it` | 0.30 | −0.1367 | 0.0964 | 1.42 | −0.4417 | 0.3152 | 1.40 |
| `it` | 0.50 | −0.2222 | 0.1544 | 1.44 | −0.6876 | 0.5372 | 1.28 |
| `it` | 1.00 | **−0.4178** | 0.2909 | 1.44 | **−0.6332** | 1.5959 | 0.40 |

Pre-rotation the same medians at `f = 1.00` were **+1.8184 / −0.0357 / +0.0590**. **Every annual
number in the rotated campaign is negative**, and the magnitude grows monotonically with `f`.

🟢 **The mechanism is the one the sweep is built on and it is not a surprise once stated.** The annual
mean of `phi_int` is held at **exactly 3.0 W/m²** at every `f` (`D-S8-2` item 5 (c)), so the sweep
cannot add energy — it only moves it in time. Rotated, the occupancy peak sits in the small hours and
the evening, which is when the heating runs, so more of the fixed gain budget lands where it displaces
heating. Four hours early, it landed where it did not. **The sign of the annual channel was a
statement about the clock, not about occupancy.**

🔴 **The two channels have swapped roles.** Annual is now the channel that stands slightly above its
spread (0.80–1.44) and peak is the one that sits below it. Neither is a comfortable margin, and §4's
verdict governs: **at `f = 1.00` nothing clears the diary spread by the margin `FINDING 134` required
of the peak claim.**

---

## 6. `FINDING 145` — THE DIURNAL SHIFT `FINDING 135` REPORTED DOES NOT REPRODUCE, BUT THE CLASS ORDERING DOES

`FINDING 135` reported the mean diurnal profile shifting **`uk` 5 → 7 and `it` 6 → 7 at `f ≥ 0.50`**.
On the rotated campaign:

| fold | `f =` 0.00 | 0.15 | 0.30 | 0.50 | 1.00 |
|---|---|---|---|---|---|
| `es` pre-rotation | 6 | 6 | 6 | 6 | 6 |
| **`es` ROTATED** | 6 | 6 | 6 | **7** | **7** |
| `uk` pre-rotation | 5 | 5 | 5 | **7** | **7** |
| **`uk` ROTATED** | 5 | 5 | 5 | 5 | 5 |
| `it` pre-rotation | 6 | 6 | 6 | **7** | **7** |
| **`it` ROTATED** | 6 | 6 | 6 | 6 | **7** |

🔴 The fold the shift belongs to has changed. **`FINDING 135`'s diurnal sentence is withdrawn and
replaced by this table.** The annual peak hour still never moves at any `f` in any fold
(`d_peak_hour_median = 0` everywhere) — that half of `FINDING 135` stands, and its explanation stands
with it: it is the thermostat recovery hour, which is set in the IDF and is not rotated.

🟢 **What DOES survive is the structural half**: the effect is monotone in dwelling class, and the
ordering is the same on both sides of the rotation.

| fold | `AB` | `MFH` | `TH` | `SFH` |
|---|---|---|---|---|
| `es` peak % | **+3.46** | +2.02 | +1.56 | +0.86 |
| `uk` peak % | **+1.04** | −0.28 | −0.40 | −0.06 |
| `it` peak % | **+0.50** | −0.42 | −0.65 | −0.63 |

The apartment block responds most in every fold, before and after. That is a claim about
surface-to-volume ratio, not about the clock, and it is the one occupancy statement this campaign
still supports.

⚪ **A recorded number that does not reproduce, flagged rather than propagated.** The Step 8 record
quotes the pre-rotation class effect as `AB` **+10.13** / +8.69 / +5.82 % against `TH` **+4.29** /
+3.06 / +2.51 %. The `uk` and `it` figures are exactly what `prerotation/agg_by_class.csv` carries;
the two `es` figures are **not**, at any level of `f` — the artefact says **7.45** and **3.89**. The
whole pre-rotation campaign is superseded so nothing turns on it, but a quoted number that its own
artefact does not carry is worth naming.

---

## 7. 🔴 `FINDING 146` — THE SAME GATE-SPECIFICATION ERROR WAS MADE TWICE IN ONE DAY

`G7.19` was written with its two phase arms scored **per dwelling as well as per bundle**. It failed
**11 of 100 CORRECT** `es` schedules on its first run. The arms are POPULATION statements: one
household that leaves for work together has its occupancy trough at exactly 07:00, and a night-shift
dwelling is legitimately empty at 05:00. The fix was to state the claim at the level it is true at and
report the per-dwelling counts as a **diagnostic with no verdict** — never to loosen the number.

🔴 **`G8.17` then reproduced the identical error**, and it was caught the same way: the first
execution of the corrected campaign returned **320 gate-unit FAILs**, every one of them
`a residential trough is the working day, not the small hours`, on schedules that were correct. Each
Step 8 run drives **one** household, so scoring a stock statistic per run is the same mistake in a
different module. `G8.17` now scores the two phase arms **once per bundle** and keeps only the
declaration arm per run.

🔴 **The durable lesson is not "check the level of aggregation".** It is that a gate written from a
correct finding inherits nothing about the level that finding is true at, and the only thing that
surfaced it both times was **running the gate on a known-good artefact and reading the failures
instead of the verdict**. A green board would have hidden the first one, and a red board nearly hid
the second as a data problem.

---

## 8. The boards, after the re-run

| | |
|---|---|
| **8.3 uninjected control** | 88 cells, 176 runs, 208.2 s, **0 severe**; **1,232 band rows, 0 gate-cell FAILs**; `control_annual.csv` **identical** to the pre-rotation run |
| **8.4 the two probes** | 6 runs, 7.2 s, 0 severe, **10 of 10 checks ok**; `G8.8` and `G8.9` each seen passing on a correct cell and failing on a broken one |
| **8.5 / 8.6 injected campaign** | **440 scenario-cells, 4,048 runs, 787.3 s, 0 severe**; **31,687 band rows, 0 gate-unit FAILs**; coverage clause **PASS** |
| **the injection battery** | **33 ok / 0 FAILED, 19 of 19 injections HIT** (was 18 of 18; `I19` is new), coverage clause PASS |
| **`G8.17`** | **PASS = 3,526** — 3,520 per-run declaration rows plus 6 bundle-level phase rows |
| **`G7.13`–`G7.17`, `G7.19`** | **6 PASS / 0 FAIL on all three folds**, battery **7 of 7**, null perturbation clean |
| **Step 7 emitter selftest** | **61 ok / 0 FAILED** (was 52) |
| **`prereg.md`** | md5 `e4243e07cdd80c9c846b91f40e3e8c45`, **unchanged** |

⚪ The one-cell probe reading that `FINDING 128` was built on also moves with everything else: annual
**−1.56 %**, peak **+3.34 %** on `es_AB_ES01` (it was +0.18 / +7.70 after `FINDING 133`'s correction).
One cell, and not a result.

---

## 8b. `FINDING 148` — the calendar probe was measured on unrotated bundles, and its peak column changes sign

`V8.i`'s probe (`tools/4thJ_step8_calendar_probe.py`, 60 runs, 11 s) is what `FINDING 131` was quoted
from, and it was measured before the rotation. Re-run on the rotated bundles:

| fold | cell | annual %, `FINDING 131` | **annual %, ROTATED** | peak %, `FINDING 131` | **peak %, ROTATED** |
|---|---|---|---|---|---|
| `es` | `es_AB_ES01` | −0.12 | **−0.1314** | +1.27 | **+0.4687** |
| `uk` | `uk_AB_GB01` | −0.04 | **−0.0175** | +0.37 | **−0.9493** |
| `it` | `it_AB_IT01` | +0.02 | **+0.0223** | −0.39 | **−0.4903** |

🟢 **The annual column is essentially unchanged**, which is what a calendar alignment should do:
shifting which weekday a diary lands on redistributes the year without adding to it.
🔴 **The peak column does not survive.** In Britain it **changes sign** (+0.37 → −0.95),
and in Spain it falls to a third of what was recorded. `FINDING 131`'s sentence — "**+1.27 / +0.37 /
−0.39 % on peak with the sign differing by fold**" — is **replaced by the row above**. The
qualitative claim it was making survives in a weaker form: the sign still differs by fold, but the
fold it is positive in has changed.

⚪ The alignment guard itself is untouched and still fires; only the number it is worth was
re-measured. `Step8_docs/outputs_step8/calendar_probe_step8.json`.

---

## 9. Decision 14, re-measured on the rotated schedules

🟢 **The null holds. `FINDING 136` survives the rotation — it is the only Step 8 result
that does.**

3 folds × 6 rule points × 5 seeds × 100 dwellings = **9,000 EnergyPlus runs, 1,576 s, 0 severe**,
all at `f = 1.00`, the sweep's upper endpoint, so this is an **upper bound** on the convention's
sensitivity.

| fold | cell | rule spread on peak, PRE-ROTATION | **rule spread on peak, ROTATED** | seed spread | ratio | `G7.18` (25 %) |
|---|---|---|---|---|---|---|
| `es` | `es_AB_ES01` | 0.178 % | **0.289 %** | 19,338.2 W | 0.458 | **not triggered** |
| `uk` | `uk_AB_GB01` | 0.075 % | **0.194 %** | 9,345.8 W | 0.410 | **not triggered** |
| `it` | `it_AB_IT01` | 0.239 % | **0.028 %** | 9,617.3 W | 0.114 | **not triggered** |

🟢 **The seed spread beats the rule spread on every metric in every fold**, exactly as before:
`peak_aggregate_w`, `p99_aggregate_w`, `max_ramp_w`, `p99_ramp_w`, `annual_heating_kwh` and
`eui_mean_kwh_m2a` all return **NOISE DOMINATES**, with ratios 0.248–0.465 (`es`),
0.075–0.482 (`uk`) and 0.114–0.422 (`it`). `trough_aggregate_w` is **DEGENERATE** in all three
folds — no variation at all — and says so rather than reporting a vacuous ratio.

🔴 **The rotation moved the absolute watts, which is how we know the fix reached this tool at
all.** `es` peak fell from about 3.25 MW to **3.06 MW** and annual heating from 2.745 GWh to
**2.664 GWh**. That check mattered: `FINDING 147` is precisely the case where it did **not** move, and
only a bit-for-bit comparison against the superseded campaign could see it.

⚪ **One comparison in `FINDING 136` no longer reads the same way, and it should not be repeated.**
The pre-rotation record said the occupancy effect was **17–60×** the whole chaining convention's
range. Against the rotated peak effects of ±**2.7145 / 0.0393 / 0.6332 %** (§4) the multiples are
**9.4× / 0.2× / 22.6×** — in Britain the occupancy channel is now **smaller** than the
convention's range. 🟢 That does not weaken decision 14: both quantities are below the
between-diary spread in `uk`, so the honest reading is that **neither is measurable there**, not that
the convention has become the larger effect. The claim decision 14 rests on is `G7.18`'s own trigger,
and it is **not approached in any fold** — 0.289 / 0.194 / 0.028 % against 25 %.

🟢 **The author's ruling of 2026-08-25 stands unchanged**: `independent`, seed 1, adopted as the
standard convention for every published Step 8 and Step 9 dataset, with the empirical null itself as
the deliverable. **No re-ruling is needed and none is requested.** Board:
`Step8_docs/outputs_step8/chaining_step8.json`, cells `chaining_step8_cells.csv`, both stamped
`"rotated_to_midnight": true` and `"diary_origin_hour": 4`.

---

## 10. What this does to the manuscript

🔴 **The occupancy result is now a null on both channels at the top of the sweep, and that is the
finding.** It is not a failure of the pipeline; it is what the pipeline measures once the clock is
right. `FINDING 125` already capped the channel from above (switching `phi_int` off entirely is worth
only +40.5 / +19.7 / +20.1 %), and the pre-registered sweep only redistributes inside that cap.

What the campaign still supports, and what it does not:

| claim | state |
|---|---|
| the effect is monotone in dwelling class, `AB` largest, in every fold | 🟢 **stands**, on both sides of the rotation |
| the annual peak hour is fixed by the thermostat, not by occupancy | 🟢 **stands** |
| the occupancy channel is a PEAK channel | 🔴 **withdrawn** — `FINDING 143` |
| occupancy injection raises annual heating demand | 🔴 **withdrawn, and the sign was wrong** — `FINDING 144` |
| the diurnal profile shifts `uk` 5 → 7 and `it` 6 → 7 | 🔴 **withdrawn** — `FINDING 145` |
| every cross-fold comparison of absolute demand | 🔴 unchanged: `FINDING 120` still governs, ±10 % |
| the comparison to TABULA | 🔴 unchanged: `FINDING 121`, `G8.7` INFO permanently |

🔴 **And the four-hour offset belongs in the methods regardless.** It crossed Step 2's ruling, Step 7's
emitter and Step 8's campaign without a single document naming it, and it was found by Step 9 asking
why a British hot-water peak sat at 03:00. That is worth one sentence in the limitations and one in
the description of the harmonisation, whatever the numbers had done.

---

## 11. Step 9 was re-run end to end, and the last obligation is discharged

⚪ **The prediction.** Step 9 rotates internally and stamps `"rotated_to_midnight": true`, so if the
Step 8 fix touched nothing outside Step 8, a full Step 9 re-run had to reproduce its output tree
bit-for-bit. Predicting a null and then measuring it is the only way that claim is worth anything.

🟢 **The measurement.** The tree was snapshotted (630 files), then `4thJ_step9_trigger.py --fold
es|uk|it`, `4thJ_step9_aggregate.py` and `4thJ_gates_step9.py --root . --offline` were re-run in
order. **`diff -rq` between the snapshot and the rebuilt `outputs_step9/` printed nothing and exited
0.** The triggers reproduced their own numbers to the digit — electricity **2244.1 / 2084.7 /
2065.4 kWh per dwelling-year**, DHW **200.79 / 201.01 / 199.47 l per dwelling-day**, **98.43 /
111.67 / 94.09 l per person-day**, `campaign run True` in every fold — and each refused to start
until all 100 presence schedules reproduced the shipped CSVs byte-for-byte, so a leak would have
stopped the run rather than changed the answer quietly.

🔴 **`FINDING 149` — and re-scoring the board caught a reporting defect that had nothing to do with
the rotation.** The runner prints `counts: {"FAIL": 3, "NOT CHECKED": 1, "PASS": 15}`. Both Step 9
documents say **16 PASS / 3 FAIL over fourteen gates and five guards** — nineteen either way, so the
missing verdict is `G9.4`'s **NOT CHECKED**, counted by hand as a pass. `V9.c` exists precisely to
stop `G9.4` reporting PASS when its DOIs do not resolve, and it does its job every run; the prose
then performed the substitution the guard forbids. **No per-gate verdict moved**, nothing was
re-thresholded, and the correction is recorded in both Step 9 documents with the original entries
left standing, the log being append-only.

⚪ **Every obligation in `D-S9-3`'s table is now discharged**, and the superseded artefacts were kept
rather than deleted (`Step8_docs/outputs_step8/prerotation/`, 22 files;
`Step7_docs/outputs_step7/schedules_bak_prerotation/`, 1,500 files) so the ruling can be revisited
against evidence if it was not what was intended.
