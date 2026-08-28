# EU-08 accounting over the D-EU-27 certified perimeter — implementation state

Task doc:   cross-session handoff from `openubem-92`, 2026-08-28 (EU-08 accounting, EU-09/EU-10 scoring over the certified 191)
Status:     EU-08 DONE · EU-09/EU-10 BLOCKED on `D-EU-28` (raised, not ruled)

## Ledger

No cluster job. No job submitted, Speed queue EMPTY. No campaign re-run: the single agreed re-run
budget was spent by OpenUBEM's `D-EU-27` execution (`scripts/campaign/run_eu_certified_rerun.py`,
1,530 cell-runs, 2026-08-28). Nothing under `openubem/` was written; all reads here are read-only.

## Verified — every number below was re-derived here from the artefact, not carried

Source: `OpenUBEM/docs/docs_ACTIVE/europeanLocations/outputs/deu27_rerun_cells.csv`
(1,531 lines = header + 1,530 rows), and the 1,185 manifests under
`OpenUBEM/openubem/outputs/eu_certified_rerun_2026-08-28/rep{1,2,3}/manifests/`.

### 1. The EU-08 execution is accountable as ours, because it consumed the ruled inputs

The re-run script pins and the manifests record, on all 1,185 attempted-cell manifests, with **zero
defects**:

| Input | Digest | Matches our driver pin |
|---|---|---|
| `eu_campaign_cell_spec_v1.1.json` | `16d3fbd6...a65f6` | yes (`D1`) |
| `2026-08-26_10.1_chaining-closure-notice.md` | `058c9d13...d74c6` | yes (`D2`) |
| `eu_cell_presence_binding_v2.json` | `8f94165d...71c99` | yes (`D4`) |

- `energyplus_version` = `23.1` on 1,185 of 1,185 (`D3` satisfied).
- `dry_run` = `false` on 1,185 of 1,185.
- `survey_fold` present on 1,185 of 1,185 — **`V8.g` is satisfied**, so `G8.16` may be scored rather
  than forced to FAIL.
- Every `f > 0` manifest carries `lift_authority.notice_sha256` = `058c9d13...` (the notice **by
  identity**, not a boolean) and `presence_source = eu_cell_presence_binding, ruled D-S10-8`,
  `presence_n_hours = 8760`. `RESUME` section 2 constraints (i), (ii), (iii) are all met by this run.
- `v1.0` was not amended. `harmonised_*.parquet` untouched.

🔴 **But the execution was NOT performed by our driver.** `tools/4thJ_step10_eu08_driver.py` pins
`RUNNER_SHA256 = 82eb7cf2...`; the `D-EU-27` timestep edit moved the runner to `4abcbf03...`, so our
driver would refuse this campaign at preflight. Our six `D`-guards were therefore **not** applied to
the certified run; the equivalent checks were re-derived here, by hand, from the manifests. This must
be said wherever EU-08 is described.

### 2. EU-08 accounting, re-derived

```
declared cells (spec v1.1)                              510
runs executed (3 replicates x 510)                    1,530
BUILD_REFUSED (D-EU-26 perimeter, deterministic)    115 x 3 = 345
attempted cells                                         395   (es 110 · uk 95 · it 190)
BUILD_REFUSED by fold                                         (es  10 · uk  85 · it  20)
completed per replicate                           341 / 346 / 342
CERTIFIED (3/3 completed, bit-identical heating,
           severe_count = 0, fatal_count = 0)           191   (es  42 · uk  75 · it  74)
rejected: not all three completed                       121
rejected: a replicate carried severe or fatal             1
rejected: replicates disagree                            82
worst disagreement among cells whose three replicates
  all completed                                       382.1 %  (uk__GB.ENG.AB.04.Gen.ReEx.001.001__f100)
archetype x fold pairs certified on all five f levels     17   (uk 8 · it 7 · es 2)
```

- **191 / 395 / 510 all reproduce exactly.** So does the 382.1 %, under
  `(max - min) / min` over cells whose three replicates all completed.
- ⚪ One partition difference, not a disagreement about the perimeter: OpenUBEM reports the
  rejections as `not_all_completed` 121 + `replicates_disagree` 83. Re-derived here the second bucket
  splits `82 + 1`, the 1 being a cell rejected on `severe_count`/`fatal_count` before its values were
  compared. `121 + 82 + 1 + 191 = 395`. The certified set is identical either way.

### 3. 🔴 FINDING 182 — the certification rule does not screen the `.err` instability markers, and the whole `es` contribution is made of cells that carry them

Of the 191 certified cells, **42 carry `Temperature out of range ... (PsyPsatFnTemp)` in all three
replicates — and all 42 are `es`.**

```
certified                          191   (es 42 · uk 75 · it 74)
certified carrying marker_psy       42   (es 42 · uk  0 · it  0)   in all 3 replicates
certified AND marker-free          149   (es  0 · uk 75 · it 74)
five-f archetype x fold pairs, marker-free   15   (uk 8 · it 7 · es 0)
```

`D-EU-27` certifies on `completed` + bitwise identity + `severe_count`/`fatal_count`. EnergyPlus
reports a diverging inside-surface heat balance as a **Warning**, so it raises neither counter — that
is precisely `FINDING 181`, and it is the reason our driver added an `eplusout.err` screen at
`last+16`. **A cell can therefore be bit-reproducible and still numerically ill-posed, and every
certified `es` cell is exactly that.** The `es` fold did not move from 0 clean to 42 certified because
the ill-posedness receded; it moved because `Timestep 12` made the same ill-posed solution
*repeatable*.

⚪ Consequence, stated without ruling on it: **`FINDING 181` is closed by construction for `uk` and
`it`, and is NOT closed for `es`.** Under the marker-free perimeter the `es` fold contributes zero,
which is the baseline position, and the five-`f` set falls from 17 pairs to 15.

🔴 This does **not** withdraw the 191. Which perimeter is quotable is a ruling, and it is OpenUBEM's
owner's — raised as **`D-EU-28`** (see Decisions).

### 4. What EU-09 can and cannot score, measured on the retained artefacts

- Retained per cell: `eplusout.csv` (8,760 hourly rows), `.eso`, `.sql`, `.err`, and a manifest.
  So **`G8.1`-`G8.4` are scoreable** — they are reproducibility gates (`D-S8-1` (a)) and the
  replicate structure is the re-run they require.
- 🔴 **The only reported variable is `Zone Ideal Loads Zone Total Heating Energy` (hourly).** There is
  no `Output:Meter` in the campaign IDFs, matching the peer's rule 6 (0 of 95 saved S2/S3 IDFs carry
  one), so **`G8.10` and `G8.11` have no data and are VACUOUS by construction, not FAIL** — and
  perturbations 3 and 4 of the Table 17 matrix cannot be seen failing. That is a reportable vacuity
  under the coverage clause, not something to be worked around.
- `V8.g` is satisfied (section 1), so `G8.16` is scoreable.

## Decisions

- **`D-EU-28` RAISED, NOT RULED (ours to raise, OpenUBEM's owner to rule).** Does the quotable
  perimeter remain the 191, or does it become the 149 marker-free cells? Recommended (b) 149, on the
  ground that `FINDING 181` is about a warning-level divergence that `severe_count` cannot see, and
  the `es` 42 are 100 % affected. Filed at
  `messages_OpenUBEM/2026-08-28_4J_to_OpenUBEM_D-EU-28_certified_perimeter_es_markers.md`.
- **EU-09 / EU-10 are NOT scored in this pass.** Every fold-level number depends on which of the two
  perimeters is ruled, and `es` is the entire difference. Scoring first and re-scoring after the
  ruling would put two perimeters into the record — the same failure the single-re-run budget exists
  to prevent.
- No new campaign run. The re-run budget is spent and is not re-opened here.

## Next

The exact next action, for a cold agent: when `D-EU-28` is ruled, build the EU-09 scorer against
Table 17 (12 perturbations) and Table 18 (`V8.a`-`V8.g`) of `MVP_european_locations.md` section 11.8,
over the ruled perimeter only, reading `eplusout.csv` per replicate from
`OpenUBEM/openubem/outputs/eu_certified_rerun_2026-08-28/rep{1,2,3}/<cell_id>/`. Score `G8.10`/`G8.11`
as VACUOUS with the reason in section 4. Then EU-10 dossier evidence over the same perimeter.

## WHAT I DID NOT VERIFY

- The `.err` files themselves were not re-parsed; the marker columns of `deu27_rerun_cells.csv` were
  taken as given. The screen they implement is ours (`last+16`) and the strings match, but the 1,530
  `.err` files were not independently re-read.
- No gate was scored, no band or threshold moved, and no G8 gate was seen failing in this pass.
- The 3J/2J trees, the manuscript notes and the board were not touched. **The board is still not
  re-published.**
- Whether `Timestep 12` is the right refinement is OpenUBEM's ruled ground (`D-EU-27`); it was not
  re-examined here.
