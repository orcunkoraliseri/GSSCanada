# B7 closed - the adapter merge drift range in the supplement

Written 2026-09-14. One edit, one file: `writing/submission/4J_supplementary_material.md:40`.
Backup: `writing/submission/previous/4J_supplementary_material.md.bak_pre_B7`.

## What the row said, and what it says now

Before: `FAIL, 4 of 4; measured 2.7e-4 to 7.3e-4 (table basis)`
After:  `FAIL, 4 of 4; measured 3.2e-4 to 7.3e-4 across those four scored runs`

The band (`below 1e-4`), the provenance letter (`H`) and the verdict (`FAIL, 4 of 4`) are untouched.
Nothing moved: this is a printed measurement corrected to the basis the row itself names.

## Why, measured rather than assumed

The row says **4 of 4**. The four scored runs are the table at
`Step4_docs/investigation/2026-08-23_G4.1_G4.3_G4.6_G4.12_four_gates_never_passed.md:41-44`:

| run | fold | `max_logit_diff` |
|---|---|---|
| 1274884 | `es` (leg 4) | `3.471e-04` |
| 1274964 | `uk` (leg 4) | `3.223e-04` |
| 1281612 | `it` (leg 4) | `3.853e-04` |
| 1286209 | `es` (leg 5) | `7.279e-04` |

Minimum `3.223e-04`, maximum `7.279e-04`. Rounded to the row's own two significant figures that is
**3.2e-4 to 7.3e-4**. The previous lower bound, `2.7e-4`, is a real measurement (`2.661e-04`) but it
belongs to a DIFFERENT run outside the four, so the row was printing a range from one basis beside a
count from another. The `(table basis)` tag flagged that the two disagreed without saying which was
being used; naming the four scored runs says it.

## A slip in the source prose, recorded and not edited out

`FINDING 103` (same document, lines 349-350 and the 2026-08-24 ledger entry) twice writes the range
as `2.7e-04`-`7.6e-04`. Every `max_logit_diff` recorded anywhere in the repository was enumerated by
grep for this note; the values are `2.498e-04`, `2.661e-04`, `3.204e-04`, `3.223e-04`, `3.471e-04`,
`3.853e-04`, `4.063e-04`, `7.019e-04`, `7.279e-04`, plus the separate `1.470e-02` and `13.71875`
readings from other checks. **There is no `7.6e-04` measurement.** The upper bound in that prose
matches no artefact; `7.279e-04` is the true maximum.

The investigation document is a historical record that deliberately keeps its own errors in place
rather than editing them away, so nothing there was changed. The slip is recorded here so the number
is not carried forward again.

## Not affected

The manuscript never prints this range (checked by grep). No figure prints it. No gate, band or
verdict moved.
