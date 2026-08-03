# improvements/investigation/deepResearch Prompts — external literature inputs for the backward audit

Three prompts, written to answer the three questions raised in
[`../3rdJ_L3_backward_audit_2026-08-03.md`](../3rdJ_L3_backward_audit_2026-08-03.md) that **cannot be
answered from project material**.

**All three reports were delivered 2026-08-03** and are folded into the audit — see the *Update
2026-08-03 (evening)* block under the audit's verdict table, the "What R*n* returned" subsection in
B-1/B-2/B-4/B-5, and the *Verification still owed* table.

| Report | Headline | Effect on the audit |
|---|---|---|
| `R1_..._report.md` | 0 of 14 study lines use `any-present × N` — but under perfect synchrony it equals sum-of-members | B-1 confirmed, **mechanism corrected** to synchrony |
| `R2_..._report.md` | No TUS↔footfall conversion exists — different denominators. GSS level and −25 % decline both internationally normal | B-4 → documentation; **B-5 re-framed as mis-specified** |
| `R3_..._report.md` | 7 of 8 authorities give no minimum-donor rule; adjustment-cell floors (n ≥ 10–20) retro-justify `MIN_POOL = 15` | **B-2 mostly closes on writing** |

All three headline answers are clean negatives. The reports are secondary syntheses — **a citation is
not evidence until it has been opened**; the audit lists nine claims owing verification.

Convention borrowed from `idf_reader/docs_ACTIVE/NUs_Journale_Revista Ingeniería de Construcción/v2/deepResearch/`
(the M and V series): scope guard first, deliverable as a populated table, a clean negative counted as
a result, and an explicit instruction that a finding weakening the paper is reported plainly.

Numbered **R** so they do not collide with the `Leg3_4-split/deepResearch/` **dr_L3-01…13** series,
which is the Leg-3 design-freeze round and is closed.

| Prompt | Question | Audit finding | Feeds |
|---|---|---|---|
| `R1_household_occupancy_aggregation_prompt.md` | How does the TUS-to-BEM literature aggregate multi-occupant households, and what does the choice cost in energy terms? | **B-1** | 2J methods + limitations (submitted paper), 3J residential channel |
| `R2_tus_presence_vs_footfall_prompt.md` | Is the ~2× gap between time-use shopping presence and retail foot traffic documented and quantified? Has a peak-normalised TUS retail schedule ever been validated against metered loads? Does ATUS show the same 25 % decline? | **B-4, B-5** | 3J retail channel, Step-4 gate re-specification, the 2030 lever reconciliation |
| `R3_donor_pool_size_criterion_prompt.md` | Does statistical matching / hot-deck imputation give a principled minimum donor-pool rule, decidable without the downstream metric? | **B-2** | 3J Step-5 methods; potentially re-selects `MIN_POOL` |

## Why these three, and not more

The other audit findings were checked against this bar and rejected as research topics:

| Finding | Why it is not a literature question |
|---|---|
| B-3 (RW1/RW2 measured off the training log) | Fixed by one 04E re-run that persists retail probabilities. Engineering, not literature |
| B-6 (ISR-raw graded PASS on a widened band) | A labelling decision the project makes itself |
| B-7 (5-seed table, ablation) | Four CPU jobs; the seeds already exist on the cluster |
| B-8 (Défaut-7 areas still in the doc body) | Documentation pass |
| B-9 (Step-5 R1 FAIL) | Needs an internal diagnostic on one driver cell, not external evidence — though R3 bears on whether R1 is a draw statistic |
| B-10 (QC hotel coverage claim) | Documentation pass; the data limitation itself is already handled correctly in code |
| B-11 (NECB densities transcribed) | Parse the IDF. Ten minutes |

## Already answered, do not re-research

Every prompt carries an instruction not to re-derive these. They are frozen and sourced in
`Leg3_4-split/deepResearch/`.

| Question | Where |
|---|---|
| Retail 2030 in-store share bands (0.90 / 0.97 / 1.05) | `dr_L3-04_instore_share_2030_REPORT.md` — R2 revisits only the *consistency* of the central value with the observed decline, not the band derivation |
| Retail and hotel EUI plausibility bands | `dr_L3-02`, `dr_L3-03` — and re-litigated again in Step 9 |
| Hotel diurnal shape and 2030 forecast | `dr_L3-05`, `dr_L3-09` |
| Output representation and exclusivity projection | `dr_L3-12` |
| Training regimen, loss balancing, backbone choice | `dr_L3-11`, `dr_L3-13` |
| Retail diurnal targets and the peak-normalisation decision | `dr_L3-06` — R2 asks whether the *validation* of that decision exists, not whether the decision was right |

One caution on `dr_L3-06`: its weekday 0.06–0.10 band is described in the design documents as
"CONFIRMED", and the measured GSS rate is roughly half of it at every cycle. R2 exists because
"CONFIRMED" and "the data says half" cannot both stand without a stated reconciliation.

## What a good report looks like

1. **A clean negative is a result.** If no study has validated a TUS-derived retail schedule against
   metered loads, or no source gives a minimum donor-pool rule, that finding is worth more than a
   plausible number with no provenance.
2. **A finding that weakens the papers is reported plainly.** Each prompt says so explicitly. R1 in
   particular can reach a paper that is already submitted; that is a reason to run it carefully, not
   a reason to soften it.
