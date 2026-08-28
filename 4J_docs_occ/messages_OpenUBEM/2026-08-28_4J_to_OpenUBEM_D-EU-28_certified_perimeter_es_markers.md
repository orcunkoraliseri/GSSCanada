# DECISION REQUEST `D-EU-28` — does the certified perimeter stay at 191, or become the 149 marker-free cells?

From: GSSCanada 4J manager session
To:   OpenUBEM owner, via `openubem-92`
Date: 2026-08-28
Status: RAISED, NOT RULED. We do not rule on this; it is a certification-rule question and the rule is yours.

---

## 1. What we were asked, and what is already delivered

EU-08 accounting is **done** and is filed at
`4J_docs_occ/Step10_docs/impl/2026-08-28_EU-08-accounting-over-the-certified-191.md`.
Your headline numbers reproduce exactly, independently, from
`deu27_rerun_cells.csv` alone:

```
1,530 runs · 510 cells · 345 BUILD_REFUSED (115 x 3) · 395 attempted
completed per replicate            341 / 346 / 342
CERTIFIED                          191   (uk 75 · it 74 · es 42)
five-f archetype x fold pairs       17   (uk 8 · it 7 · es 2)
worst disagreement among all-3-completed cells   382.1 %  uk__GB.ENG.AB.04.Gen.ReEx.001.001__f100
```

All 1,185 attempted-cell manifests are identity-clean: spec `16d3fbd6...`, binding `8f94165d...`,
notice `058c9d13...`, `energyplus_version` `23.1`, `dry_run` false, `survey_fold` present on every
one, and every `f > 0` manifest carries the chaining notice **by digest** rather than as a boolean.
One partition difference, immaterial to the perimeter: we split your `replicates_disagree` 83 into
82 disagreements + 1 cell rejected earlier on `severe_count`/`fatal_count`. `121 + 82 + 1 + 191 = 395`.

**EU-09 and EU-10 are not scored yet, and this request is the reason.**

## 2. The finding

`D-EU-27` certifies on a conjunction of `completed`, bitwise-identical `heating_kwh`,
`severe_count = 0` and `fatal_count = 0`. It does **not** screen the `eplusout.err` instability
markers.

Of the 191 certified cells, **42 carry `Temperature out of range ... (PsyPsatFnTemp)` in all three
replicates, and all 42 are `es`**:

```
certified                                    191   (uk 75 · it 74 · es 42)
certified carrying marker_psy in all 3 reps   42   (uk  0 · it  0 · es 42)
certified AND marker-free                    149   (uk 75 · it 74 · es  0)
five-f archetype x fold pairs, marker-free    15   (uk  8 · it  7 · es  0)
```

EnergyPlus reports a diverging inside-surface heat balance as a **Warning**, so it raises neither
counter the certification rule reads. That is `FINDING 181` itself. So on our reading the `es` fold
did not move from 0 clean to 42 certified because the ill-posedness receded — `Timestep 12` made the
same ill-posed solution *repeatable*, which is a different property. Recorded on our side as
`FINDING 182`.

We are not disputing `D-EU-27`. The rule does what it says; the question is whether the set it
selects is the set that may be quoted.

## 3. The decision

**Which perimeter is quotable for EU-09 / EU-10?**

- **(a) Keep 191.** Certification is bit-reproducibility plus a clean severity count, and warnings
  are not part of the contract. `es` is retained at 42; the five-`f` set stays 17.
- **(b) Restrict to 149 marker-free cells.** *(our recommendation)* `FINDING 181` is by definition a
  warning-level divergence that `severe_count` cannot see, the affected set is 100 % of certified
  `es`, and this is exactly the screen your own runner already emits into the CSV — no new
  measurement, no re-run, one filter on an existing column. `es` contributes 0; the five-`f` set
  falls to 15 pairs.
- **(c) Report both, and let each downstream claim state which it used.** We would argue against
  this: two perimeters in the record is the failure the single-re-run budget exists to prevent.

Whichever you rule, `D-EU-26` stands independently — `uk` loses 17 of 36 archetypes and no `uk`
fold-level or nationally representative heating figure may ever be quoted.

## 4. One thing that is not a decision, but must be recorded either way

The campaign IDFs report a single variable, `Zone Ideal Loads Zone Total Heating Energy` (hourly,
8,760 rows per cell), and carry no `Output:Meter` — consistent with your rule 6. So **`G8.10` and
`G8.11` are VACUOUS by construction, not FAIL**, and perturbations 3 and 4 of the Table 17 matrix
(`MVP_european_locations.md` section 11.8) cannot be seen failing on these artefacts. We will report
that as a vacuity in EU-09 rather than work around it, unless you tell us otherwise.

## 5. What happens next on our side

Nothing runs and nothing is written under `openubem/`. On a ruling, EU-09 is built against Table 17
and Table 18 over the ruled perimeter only, then EU-10. No campaign re-run is requested and the spent
budget is not re-opened.
