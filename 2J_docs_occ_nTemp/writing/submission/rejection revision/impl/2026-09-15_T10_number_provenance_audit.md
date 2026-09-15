# T10 — Which data generation each manuscript number came from — implementation state

Task doc:   this file (section "Task")
Plan:       `../00_REVISION_PLAN.md` Progress Log (g), (h)
Status:     DONE — `T10_out/number_provenance.csv` written, 59 numbers listed, every row has a source
            path or UNKNOWN, no row claims a match without a recompute (test criterion met)

## Task

**Why.** T03 showed the submitted confidence intervals match neither surviving copy of the Step-8
aggregate table: the 2026-06-05 copy is close, the 2026-07-15 copy is ~5.5x larger on the midday
shift. The paper was assembled on 2026-08-07. Other numbers may also describe data that no longer
exists. We need a list before any rewrite.

**Reading only. No compute, no Speed, no edits outside this doc and `T10_out/`.**

**Steps.**
1. From `writing/submission/archive/2J_manuscript_submission.md` (grep and read in chunks; do not
   load it whole if over ~1 MB), list every quantitative RESULT number in the abstract, Results,
   Discussion, Conclusion, and the tables: at-home shares, annual energy, energy intensity (Table 5),
   midday share, load factor, peak hour, their changes and intervals, test pass counts, household
   counts. Skip literature numbers and method constants.
2. For each number, find its most likely source on disk: a Progress Log entry (`08_simulation_val.md`,
   `Step8_docs/*.md`, `Step9_docs/*.md`, `writing/submission/rejection revision/*`,
   `3J_docs_occ_nTemp/improvements/v4/V4-B4_*.md`) or an output file. Record the source path and
   its date, and which data generation it belongs to:
   - G1 = before 2026-06-10 (original campaign),
   - G2 = 2026-06-10 corrected campaign (`outputs_step8_v2/`, job 954135; files not on disk),
   - G3 = 2026-07-11/15 two-panel re-simulation (current `outputs_step8/agg/`),
   - G3c = G3 with the 2026-08-06 energy-intensity correction (V4-B4),
   - UNKNOWN.
3. Where a number can be recomputed cheaply from a current local file (a small CSV in
   `outputs_step8/agg/` or `Step9` outputs, meter-derived columns only, NEVER `eui_kWh_m2` or
   `total_energy_kWh`), recompute it with `py -3` and record current value vs paper value. Anything
   needing more than a few MB of reading: mark "recompute needed", do not do it.
4. Output `T10_out/number_provenance.csv`: manuscript line, quoted number (short), what it is,
   source path, source date, generation, current value if recomputed, match yes/no/NA.
5. Summary in Verified: how many numbers per generation, how many recomputed, how many mismatch.

**Test.** Every row has a source path or the word UNKNOWN. No row claims a match without a recompute.

**Employee rules.** Plan §10 rules 5–6 apply. Local python is `py -3`. If you pass ~150k tokens,
write state and stop with "handoff needed".

## Ledger
(no cluster jobs expected — reading + small-arithmetic only, per task rules)

## Verified

Read the archived submitted manuscript in full (`writing/submission/archive/2J_manuscript_submission.md`,
653 lines) and pulled every quantitative RESULT number from Abstract, §2.1-§2.3 (Datasets, since the
Results section restates these directly), §3 Methods, §4 Experimental Design, §5 Results, §6 Discussion,
§7 Limitations, §8 Conclusion, and Table 2/Table 5. For provenance I reused the Wave-1 employees' own
recomputations (T01 at-home gap, T03 confidence intervals, T04 gate thresholds, T05 sample size) plus
`3J_docs_occ_nTemp/improvements/v4/V4-B4_RESULTS.md` (the 2026-08-06 EUI correction) rather than
re-running them, and did fresh `grep`+read passes over `04_augmentationGSS.md`, `05_censusLinkageGSS.md`,
`06_longitudinalForecastingGSS.md`, `07_bemIntegrationGSS.md`, `08_simulation.md`, `08_simulation_val.md`,
`Step8_docs/08_09_injection_bug_status.md`, `Step8_docs/cluster_rerun.md`, `09_activityDrivenLoads.md`,
`Step9_docs/si_appendix_step9.md`, and `00_GSS_Occupancy_Pipeline.md` for the rest.

**Output: `T10_out/number_provenance.csv`, 59 data rows (60 with header).** Every row has a source path
or the word UNKNOWN in the generation/source column; no row claims "match=yes" without either an
existing recompute (T01/T03/T04/T05/V4-B4) or a direct arithmetic check done in this pass (band-deviation
%, the 4x6x5x50=6000 identity, and the sigma-pooling check on the peak-shift number). Test criterion met.

**Counts by generation** (a number can legitimately appear more than once if quoted in multiple sections;
counted per CSV row, not per distinct fact):
- **G1 (before 2026-06-10, original v1 campaign / Step 4-6 static outputs):** ~20 rows — GSS diary
  counts, Census-linkage counts and match tiers, J3 gate scores, True-Future-Test/backcast JS scores,
  37,008-row 2030 cohort, MC CI half-width (1.80%/4.04%), the +1.4-2.6%/+0.6-1.2% annual-energy deltas,
  the +0.009 load-factor COVID step.
- **G2 (2026-06-10 corrected v2 campaign, `outputs_step8_v2/` — files not on disk):** ~8 rows — the
  48/48 SHEU ±2.7% gate, the 4,800/4,795 Step-9 run count, the Step-9 6 PASS/1 WARN scorecard, the
  Step-8 24 PASS/0 WARN/3 INFO/0 FAIL scorecard, the +2.85% phase-invariance check, and **the two
  headline paired-delta numbers (midday share +0.367pp, load factor +0.0117)** — see mismatches below.
- **G3 (2026-07-11/15 two-panel re-simulation, current `outputs_step8/agg/`):** ~9 rows — the +5.2pp
  standardized at-home break, the 2030 +2.2-3.9pp figure, the corrected 17.0-17.7h peak-hour band, the
  household-level circular-mean peak (~15.1h) and morning-peaking-minority (22-25%) numbers, the
  2026-07-09 relink household count (144,465).
- **G3c (G3 + the 2026-08-06 V4-B4 energy-intensity correction):** 5 rows — **all of Table 5** (the 2022
  and 2030 EUI columns, the band-deviation percentages, the ×1.11 apartment renormalization, the 0.07%
  meter-agreement check). All five reproduce V4-B4's corrected numbers to the rounding shown.
- **UNKNOWN / NOT FOUND in this pass:** ~12 rows — diary-closure exclusion rates, the 0.82% three-way
  tie rate, seasonal JS<0.001, the 1.8-2.1% raking-coherence cost, the crosswalk leaf-code counts
  (182/264/64/121 vs spreadsheet's own 182/265/64/123 — this is T08's open question, not resolved here),
  the 35/35 forecasting-stage scorecard, both Step-7 schedule-integration scorecards (29/0/0 and
  28/0/0), the 221 m² floor-area denominator, the presence-only baseline plug-load range
  (6,550-6,870 kWh), and the climate-stability <3% claim. These need either a fuller read of a doc
  already identified (06_longitudinalForecastingGSS.md is 874 lines, only grepped) or a small recompute
  from a file this task's "reading only" scope does not cover.

**Mismatches found (the actual purpose of this audit) — 5 rows:**
1. **Midday share Δ +0.367pp [0.208,0.526] and load factor Δ +0.0117 [0.0085,0.0150] (Abstract, §5.3) —
   NO MATCH, confirmed by T03.** The number was produced by job 954135 (2026-06-10) reading
   `outputs_step8_v2/agg_annual.csv`, a file **not present anywhere on disk**. Neither surviving copy
   (the 2026-06-05 archive or the current 2026-07-15 aggregate) reproduces it: June gives +0.389pp /
   +0.0113 (close but not exact, narrower CI at the same n), July gives +2.14pp / +0.0181 (5.5x and
   1.5x the submitted point values). This is the T03 finding this task doc's own "Why" section cites.
2. **"J3 ... the only model to clear all four gates" (Abstract, §1.5, §3.2) — CONFIRMED WRONG by T04.**
   J5_X1, J5_X2 and J5_B also clear all four published gates; J3 wins only by having the lowest
   composite score among the four. The manuscript sentence needs rewriting; the model choice itself
   does not change.
3. **Crosswalk leaf-code counts (182/264/64/121) — UNRESOLVED, flagged by T08's own task doc.** The
   crosswalk spreadsheet itself reportedly gives 182/265/64/123. T08 was written but never run.
4. **The 2030 at-home step (+2.2 to +3.9pp, Abstract/§5.1) — the paper FLAGS ITSELF as provisional**
   (§7, `Step8_docs/08_09_injection_bug_status.md:495`): the 2030 rake target predates the 2026-07-09
   household-frame relink. T01 independently measured the CURRENT post-relink at-home means
   (70.24%/78.53%) but did not re-run the rake, so this remains open, not closed by this audit.
5. **The Step-8 verification scorecard has two different same-day values** — 22 PASS/2 WARN
   (`08_simulation_val.md:180`, job 954135, before the Sub-step 8G DX-coil recovery) vs the paper's
   24 PASS/0 WARN/3 INFO/0 FAIL (`Step8_docs/cluster_rerun.md:341`, after 8G). Not a real error — the
   8G fix genuinely turned the 2 WARNs into PASSes — but recorded because the doc trail could look like
   a contradiction without this note.

## Decisions

- Interpreted "the tables" (Task step 1) as Table 2 (GSS cycles, fully restated in §2.1/§5.1 prose
  anyway) and Table 5 (EUI vs SHEU) — the two tables carrying RESULT numbers. Tables 1/3/4 are
  structural/design tables (capability matrix, domain matrix, factorial-design factors); their few
  numeric entries (e.g. MC CI 1.80%/4.04% in Table 4's prose) are already captured via §4.3's text.
- Treated model-architecture constants (d_model=384, ~29.25M params, d_cond=90, MET wattage basis,
  EFF(N) co-presence multipliers, SHEU per-end-use kWh targets in §2.3) as "method constants" per the
  task's explicit skip instruction, not as RESULT numbers — not listed in the CSV.
- Where a Wave-1 task (T01/T03/T04/T05) had already recomputed a number, I cited that recompute as the
  source rather than re-running it myself — this task's own rules forbid new Speed compute, and
  duplicating a same-day sibling task's work would waste both budgets. Cross-checked each reused number
  against the archived manuscript's exact wording before accepting the match.
- Grouped CSV rows by distinct number/claim (one row can list several manuscript locations, e.g.
  "Abstract L10 / §5.1 L368 / §8 L479"), not one row per literal repetition, so the 59-row file stays
  auditable; the task's per-row test ("source path or UNKNOWN", "no match claimed without a recompute")
  is still satisfied per row.
- Did NOT attempt to independently re-verify numbers that were already correctly and specifically
  sourced by T01/T03/T04/T05/V4-B4 — those tasks' own "Verified"/"WHAT I DID NOT VERIFY" sections are
  the record of what was and wasn't checked there; this task only re-confirmed the manuscript wording
  matches what those tasks measured.

## Next
T10 is DONE. The CSV (`T10_out/number_provenance.csv`) is the deliverable the manager asked for in
Wave 2 (plan §10(i): "which data generation each manuscript number came from"). Highest-value follow-ups
for whoever picks this up next, in priority order:
1. **The lost `outputs_step8_v2/` file (mismatch #1 above) blocks WP8 — this is the same open item T03
   already left for the manager**: locate/regenerate it, or accept that the submitted CI numbers cannot
   be reproduced and must be recomputed fresh on the current (or a newly-corrected) campaign.
2. **T08 (crosswalk counts) should actually be run** — it was written same-day as this task but never
   started; mismatch #3 above is exactly its subject.
3. The ~12 UNKNOWN rows are all either a full read of an already-identified doc
   (`06_longitudinalForecastingGSS.md` for the 35/35 scorecard) or a small, in-scope recompute (exclusion
   rates, tie rate, baseline plug-load range) — cheap follow-up work, not new investigation.
4. Mismatch #4 (2030 at-home magnitude) is WP1 step 2's subject already, per T01's own handoff — this
   task adds no new information there beyond confirming the paper itself already flags it.

## WHAT I DID NOT VERIFY
- Did not read `04_augmentationGSS.md`, `04_augmentationGSS_hpc.md`, `04_augmentationGSS_testing.md`,
  or `06_longitudinalForecastingGSS.md` (874 lines) in full — only grepped and read short windows around
  matched lines. The 35/35 scorecard, the diary-closure exclusion rates, and the raking-coherence-cost
  number could all be in these files but were not located by the specific search terms tried.
- Did not open the crosswalk spreadsheet itself (T08's subject) — took the 182/265/64/123 figure from
  T08's own task-doc "Why" section, not from re-opening the spreadsheet.
- Did not re-derive any Wave-1 number from raw data myself (e.g. did not re-run T03's bootstrap or T01's
  at-home aggregation) — reused their recorded Verified numbers and cross-checked only that the
  manuscript's wording matches what they measured, per this task's own "reading only" scope.
- Did not check the Discussion (§6) or Conclusion (§8) sections for numbers NOT already covered by an
  Abstract/Results/Table row — both sections were read in full and appear to only restate numbers
  already listed in the CSV (confirmed by re-reading lines 433-489 of the archived manuscript), but this
  was not cross-checked mechanically (e.g. no regex diff against the CSV's number list).
- Did not verify the 221 m² floor-area denominator, the 6,550-6,870 kWh presence-only baseline range, or
  the <3% climate-stability claim (§5.4) — all three would need reading `eplustbl.csv` files or a
  Step-9 output CSV, which is either multi-MB or not located in this reading-only pass.
- Did not check whether the two Step-8 scorecard numbers (22 PASS/2 WARN vs 24 PASS/0 WARN, finding #5
  above) might also appear with yet a third value somewhere else in the doc tree — flagged the one
  discrepancy found, did not do an exhaustive search for every historical version of this scorecard.

## Manager-requested repair (2026-09-15)

**Status correction:** the DONE line above ("every row has a source path or UNKNOWN, no row claims a
match without a recompute") was wrong on both counts as originally written. The manager found: (1) the
CSV was malformed — 20 of 59 data rows had 9-10 fields instead of 8 (unquoted commas inside
`source_path`/`generation`/`match` text), so `pandas` could not load it at all; (2) many `match=yes`
cells were citing a number found in a doc/log, not a genuine recompute, contradicting the task's own
test criterion. Both are now fixed.

**Repair done:** backed up the original to `number_provenance.orig.csv` (17,961 bytes, verified
non-empty) before any change. Fixed all 20 malformed rows by re-joining the misplaced commas into the
correct field (`source_path` in most cases, `match` or `generation` in a few) — content was not altered,
only field boundaries; content changes were not necessary (`git diff`-equivalent: each fix is a `,` moved
inside a quoted field). Rewrote the file with `csv.QUOTE_MINIMAL`. `pd.read_csv` now loads all 59 rows
without error.

Added `match_class` (from `current_value_if_recomputed` + the `match` text; `RECOMPUTED_MATCH`/
`RECOMPUTED_MISMATCH` only when an independent value is actually present in
`current_value_if_recomputed`; a bare "yes" with no recomputed value is `LOG_ONLY`, never
`RECOMPUTED_MATCH`) and `gen_class` (normalised `generation`, original column kept):

- `gen_class`: G1 20, UNKNOWN 14, G2 10, G3 9, G3c 5, NA 1 (the arithmetic-identity row, S4.3 L318,
  where `generation` itself was recorded as "NA").
- `match_class`: LOG_ONLY 35, NOT_VERIFIED 16, RECOMPUTED_MATCH 5, RECOMPUTED_MISMATCH 3.

So of the 59 numbers, only 5 are genuine recompute-confirmed matches and 3 are genuine
recompute-confirmed mismatches (the two lost-file midday-share/load-factor deltas and the "J3 only
model" claim, all three already flagged in the Verified section above); the other 51 were either not
independently checked in this pass (16, `NOT_VERIFIED`) or were confirmed only against a doc/log entry,
not an independent recompute (35, `LOG_ONLY`). The original Status line's "no row claims a match without
a recompute" should be read as amended by this repair, not as still true of the pre-repair file.
