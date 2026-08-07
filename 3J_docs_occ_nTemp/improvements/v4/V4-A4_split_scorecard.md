# V4-A4 — `S9-EUI-*` scored per geometry, under the split authorised by V4-A1

**2026-08-06 · desk work · no simulation, no band edit, no re-run, cluster not contacted.**
Generator: `improvements/v4/a4_split_score.py` · machine-readable result:
`improvements/v4/v4_a4_split_scorecard.json`.
🔴 **`Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_gates.json` was NOT written to.** This is
a side scorecard. The shipped gate statuses are unchanged.

---

## 0. 🔴 Read this before the tables: the input was wrong, and it was my error

**A4's four fences included two written sub-verdicts — `Tall` PASS, `SuperTall` FAIL — recorded before
the V4-A1 decision was taken. Both are wrong. The measured result is the exact inverse.**

Under the pre-registration that is *"the finding, not a correction"*, and the finding is this: **the
predictions were not computed on the artefact that ships.** They came from
`Leg3_4-split/Step9_docs/outputs_step9/` (**2026-07-31 11:42**), which is a *sibling* of the frozen
deliverable `outputs_step9_deliverable/` (**2026-08-06 00:05**) — the directory named as the
deliverable in `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md` and used throughout v3.

**The superseded directory predates the v2 decisions and, more importantly, predates `V2-D10` — the
per-object `LAUNDRY` resize — which is the change that moved this channel.** §3 below re-runs the
identical scoring on that superseded file and **reproduces both predictions exactly**. That is the
proof: the predictions were right about the wrong artefact.

⚠️ **This defect is not confined to A4.** `V4-A2` and `V4-A3`, closed earlier the same day, were
computed from the same superseded file. Their **conclusions survive** for office and retail (the two
files differ by ~0.1 % there) but the **hotel numbers in them are wrong in both magnitude and
direction**, and `V4-A2`'s "Finding 2" accused the master pipeline document of an inversion that the
deliverable shows **the document was right about**. That retraction is §5.

---

## 1. The result — every channel, both units

### office (rule in force = `all_cells`, band [100, 200])

| unit | n | median | range | in band | below floor | above ceiling | verdict |
|---|--:|--:|---|--:|--:|--:|---|
| **pooled (as shipped)** | 56 | 71.02 | 61.72–90.21 | 0 | 56 | 0 | **FAIL** |
| SuperTall | 28 | 73.85 | 64.16–90.21 | 0 | 28 | 0 | **FAIL** |
| Tall | 28 | 70.47 | 61.72–88.43 | 0 | 28 | 0 | **FAIL** |

### retail (rule in force = `median`, band [80, 155])

| unit | n | median | range | in band | below floor | above ceiling | verdict |
|---|--:|--:|---|--:|--:|--:|---|
| **pooled (as shipped)** | 56 | 75.63 | 63.63–96.84 | 12 | 44 | 0 | **FAIL** |
| SuperTall | 28 | 74.99 | 63.63–94.80 | 6 | 22 | 0 | **FAIL** |
| Tall | 28 | 76.47 | 63.63–96.84 | 6 | 22 | 0 | **FAIL** |

### hotel (rule in force = `all_cells`, band [180, 300])

| unit | n | median | range | in band | below floor | above ceiling | verdict |
|---|--:|--:|---|--:|--:|--:|---|
| **pooled (as shipped)** | 56 | 260.54 | 203.33–318.42 | 28 | 0 | 28 | **FAIL** |
| SuperTall | 28 | 210.45 | 203.33–218.22 | 28 | 0 | 0 | **PASS** |
| Tall | 28 | 310.15 | 302.86–318.42 | 0 | 0 | 28 | **FAIL** |

**Each channel is scored under its own rule in force**, read off the deliverable's own gate text, not
under a uniform rule. For retail the two rules agree here anyway: both sub-medians are under the 80
floor, so `all_cells` would also return FAIL twice.

---

## 2. The four fences, checked one by one

| # | fence | result |
|---|---|---|
| 1 | **Written first, scored second.** `Tall` PASS / `SuperTall` FAIL | 🔴 **BOTH FAILED — inverted.** Cause established in §0/§3, not explained away |
| 2 | **The scorecard must not lose a FAIL.** At least one hotel sub-gate still FAILs | ✅ **HELD.** `Tall` FAILs 28/28, all above the 300 ceiling. **The split does not clear a blocker** |
| 3 | **All three channels, not just the one it helps** | ✅ **DONE.** Office and retail were scored per geometry too |
| 4 | **Desk work only** | ✅ One CSV read, one new file written. No sim, no band edit, cluster not contacted |

**Fence 3's reported result is that the split changes nothing for office or retail.** Both sub-gates
FAIL in both channels, identically to the pooled gate. That is the outcome, not a reason the work was
skippable — a split that only ever fires on the channel it was proposed for would be a unit chosen to
fit one answer.

### Is the split adopted?

**Yes for hotel, and it is adopted on stronger evidence than it was authorised on, not weaker.**
Fence 1 fired, and the pre-registration says the split is not adopted *until the disagreement is
explained*. It is explained, and the explanation is a wrong input file rather than a wrong idea about
the data. The structural claim that motivated the split — **the hotel population is bimodal and the
pooled median describes no building in the set** — is not merely intact on the deliverable, it is
**substantially larger** there (§4).

**For office and retail the split is scored and reported, and it buys nothing.** Recording that is the
point of fence 3.

---

## 3. The proof that the input, not the reasoning, was wrong

The identical scoring run against the superseded `outputs_step9/`:

| channel | unit | median | range | verdict |
|---|---|--:|---|---|
| hotel | pooled | 178.29 | 147.87–209.43 | FAIL |
| hotel | SuperTall | 154.97 | 147.87–162.76 | **FAIL** |
| hotel | Tall | 201.12 | 193.83–209.43 | **PASS** |

**That is the pre-registered prediction, exactly.** `Tall` PASS, `SuperTall` FAIL. The prediction was a
correct reading of the file it was made from.

🔴 **And the inversion was already on the record before I re-derived it wrongly.** The v2 closure
prompt, `3rdJ_L3_manager_prompt_2026-08-06_v2_close.md` §V2-E5, states it in terms:

> `S9-EUI-hotel` reads **28/56 in both arms**, and **all 28 turned over**: base **28 below** the floor
> / 0 above → deliverable **0 below / 28 ABOVE** the ceiling, median **178.29 → 260.54**. *The failing
> end inverted while the count held still.*

**The count 28 holding still across the inversion is exactly what made the stale file look plausible.**
Both artefacts report "28 of 56" for this gate. The number that would have caught the substitution —
the direction — was the number I then used to declare the document wrong.

---

## 4. What the split actually shows on the canonical data

| | superseded (wrong input) | **frozen deliverable (canonical)** |
|---|---|---|
| clusters | SuperTall 147.87–162.76 · Tall 193.83–209.43 | **SuperTall 203.33–218.22 · Tall 302.86–318.42** |
| largest empty gap | 31.07 kWh/m²/yr = 25.9 % of the band | **84.64 kWh/m²/yr = 70.5 % of the band** |
| which boundary sits in the gap | the **180 floor** | **the 300 ceiling** |
| pooled median | 178.29, in the gap | **260.54, in the gap** |
| which geometry fails, and at which end | SuperTall, below the floor | **Tall, above the ceiling** |

**The finding that motivated the split is stronger on the canonical data, not weaker.** The empty gap
is **70.5 % of the entire band width**. Two thirds of the band contains no building.

### The gate is still blind to occupancy, and now the control says so directly

Injection moved against its own uninjected `Default_NECB` control, per `building × city`:

| geometry | city | uninjected control | injection then moves it | as % |
|---|---|--:|---|---|
| SuperTall | CLG | 204.83 | −1.50 … +0.87 | −0.73 % … +0.42 % |
| SuperTall | MTL | 216.06 | −0.86 … +2.17 | −0.40 % … +1.00 % |
| Tall | CLG | **304.41** | −1.55 … +0.78 | −0.51 % … +0.26 % |
| Tall | MTL | **315.82** | −0.70 … +2.60 | −0.22 % … +0.82 % |

🔴 **Both `Tall` controls are already above the 300 ceiling before any occupancy is injected, and both
`SuperTall` controls are already inside the band.** Every sub-verdict in §1's hotel table is therefore
**set by the untreated control**, and the occupancy model moves each cell by **at most 1.00 %** against
a gap of 84.64. `S9-EUI-hotel` returns the same verdict with and without the model it is named for —
on either artefact, in either direction, in every unit.

⚖️ **So the limitation survives its own decision, exactly as §4.1 of the plan said it would.** The
split buys correct **attribution**: it stops one number standing for two populations that share no
values, and it names the axis — geometry — that the verdict is actually on. **It does not make this
gate informative about occupancy.** That sentence stays in the pipeline document whatever the split
returns.

---

## 5. Retraction — `V4-A2` Finding 2 was wrong, and the document was right

Finding 2 asserted that `3rdJ_00_4split_Occupancy_Pipeline.md` described the hotel failures inverted in
three places, and struck three passages reading *"21 of 56, all over the ceiling, all `Tall`, zero
`SuperTall`"*.

**Against the frozen deliverable, the struck clauses are correct.** The failures are **above the
ceiling**, they are **`Tall`-only**, and there are **zero `SuperTall`** — `verdict_asmodelled` in the
deliverable CSV tallies `Tall` 28 FAIL / `SuperTall` 28 PASS. **My correction imported a number from a
neighbouring artefact without its label — which is precisely the defect the correction accused the
document of.** Third instance in three days, and this one is mine.

**One part of the original text is genuinely wrong, and it is the count.** The deliverable reports
**28 of 56** outside the band on the CFA basis, not 21. On the GFA-share basis it is 14. **21 matches
neither basis**, so it is not a basis mix-up and its provenance is not established here.

Sites, all corrected additively — my strike is itself struck, the original restored, and only the
count carries a correction:

- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md` lines ~422, ~574, ~649
- `improvements/v4/3rdJ_L3_v4_implementation.md` §2.2 Finding 2
- `improvements/prompts/3rdJ_L3_manager_prompt_2026-08-06_v4_open.md` §3 Finding 2

⚠️ **Resolved OPEN DECISION 6 (hotel amenity zones) is restored to its original footing.** Finding 2
had recorded that it argued from an inverted clause. It did not; it argued from the deliverable. Its
conclusion stands, and it now stands on the evidence it actually cited.

---

## 6. What did not move

**No gate status, no band value, no rule, no threshold.** `step9_gates.json` is untouched in both
directories. All three `S9-EUI-*` remain **FAIL** — the pooled hotel gate FAILs under `all_cells`
whether or not the split is adopted, because `Tall` is 28/28 over the ceiling.

🔴 **And the counterfactual the deliverable already discloses is unchanged by this task:** under the
`median` rule the pooled hotel gate would **PASS** (260.54 is inside [180, 300]). That is recorded, not
proposed. **A gate is never resolved by picking the rule that passes** (R1, 2026-07-21).

## 7. Reopen trigger

**If any future work re-derives a Step-9 number, it must state which of the two `outputs_step9*`
directories it read.** A figure quoted without that label is not accepted, including from me. The
count `21` is unexplained and stays flagged until its provenance is found or the claim is dropped.
