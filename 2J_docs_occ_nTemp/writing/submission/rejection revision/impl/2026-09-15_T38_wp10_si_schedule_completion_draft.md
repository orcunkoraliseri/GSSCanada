# T38 — WP10: SI draft, schedule completion and donor draw, every number traced

Task doc and implementation state in one file. Written by the manager 2026-09-15 (plan log (ba)).
Agent: Sonnet, fresh session. **Local reading and writing only. No cluster. No cluster commands at all.**

## Aim
Write the second Supplementary Information part: `rejection revision/manuscript/draft_SI_schedule_completion.md`.
It covers how a household's diary is completed into a full-year schedule and how donor days are drawn, which the
first SI part (`draft_SI_model_selection.md`, T36) deliberately left out and pointed here. Reviewer 1 asked for
the completion step to be reproducible; this part must let a reader reproduce it from the text alone.

## Inputs (read; do not edit)
- `../manuscript/draft_SI_model_selection.md` — read it first, in full. It is the sibling part: match its voice,
  its section numbering style, and its number-trace-table format, and do not repeat what it already says.
- `../manuscript/prep/si_move_list.md` — the rows assigned to schedule completion / donor draw.
- `../../archive/2J_manuscript_submission.md` — only the line ranges that describe completion and donor draw
  (find them with `grep -n`, then read with offset/limit).
- Project step docs under `2J_docs_occ_nTemp/`: the day-type stratification, the donor pool definition, the draw
  rule and its seed, the annual assembly, and the 5-min to hourly reduction for EnergyPlus. Find each with
  `grep -rn` on the exact value or phrase; never open a multi-MB file whole.
- `impl/2026-09-15_T24_historic_cycle_schedules_donors.md` for the donor-draw history.

## Content
1. What a completed schedule is: from one diary day to 8,760 hourly values, stated so a reader could rebuild it.
2. Day-type strata and why weekday, Saturday and Sunday are handled separately.
3. The donor pool: who is eligible to donate a day, and what is matched on.
4. The draw rule: deterministic given the seed; state the seed and what it controls.
5. **The sampling-pool caveat, stated plainly**: the pool is the set of households passing the schedule sanity
   check on the loaded file, so it depends on the schedule content itself. On the rebuilt schedules the pool
   differs from the published one (16,326 against 16,208 in one cell, 320 households) and the same seed therefore
   draws a different sample. Say what this does and does not affect. Source: plan log (ak) and the T21 task doc.
6. Assembly to the full year and the reduction to the resolution EnergyPlus reads.
7. A **number trace table**: value · meaning · source file:line where you read it · matches the archived text
   (yes / no, give both) · NOT FOUND if no source file exists.

## Rules
- Plain words. Labels banned in prose: J3, True-Future-Test, frozen frame, Tier-1/2/3, FailSafe, COLLECT_MODE,
  DDAY_STRATA, Step-8, Step-9, occACT, gate, PASS/WARN/INFO, Nb-f, T-numbers. Say "the chosen model",
  "the sanity check", "the rebuilt schedules".
- Prose says **limitation**, never failure. Never relax or restate a band to make something pass.
- **Ruling (b) applies**: no old-campaign number appears. If the text needs a number only the rebuilt runs produce,
  write `[VALUE PENDING: <what is needed, which run produces it>]` and list it as PENDING in the trace table.
- If a value has no source file, keep it out of the prose and list it NOT FOUND. If the source disagrees with the
  archived manuscript, the source wins and you record both.
- No em dashes, no en dashes. Write only `manuscript/draft_SI_schedule_completion.md` and this file. Do not edit
  the plan, the archive, the code, other task docs, or any submission file.
- Never run `mkdir`, `find`, `du`, `md5sum`, `cp`, or any python on the Speed login node. This task does not touch
  the cluster at all. Never open a multi-MB file whole: `grep -n`, `head`, `wc -l`, offset/limit reads.
- Append to Ledger and Verified as you go. End the turn when the draft exists; do not wait for anything.

## Ledger
- No cluster jobs run by this task (local reading/writing only, as required). One cluster-produced
  number reused read-only via an earlier task's already-collected output: job 1328414's sampling-pool
  sizes, via `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-438`.
- Read the sibling SI part (`manuscript/draft_SI_model_selection.md`, full) first for voice and
  trace-table format, per the task rule.
- Read `manuscript/prep/si_move_list.md` (full), `archive/2J_manuscript_submission.md:240-319`
  (offset/limit), `impl/2026-09-15_T24_historic_cycle_schedules_donors.md` (full), and
  `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:355-454` (offset/limit) plus `00_REVISION_PLAN.md:940-980`
  (offset/limit) for the sampling-pool caveat's history.
- Read `07_bemIntegrationGSS.md` (full, 240 lines) and `07_aug_to_bem.py` (full, 235 lines) as the
  primary sources for the schedule-completion / donor-draw mechanism. Read cited ranges only (not
  whole files) of `Step8_docs/08_gen_cycle_schedules.py`, `eSim_bem_utils_2J/integration.py`,
  `eSim_bem_utils_2J/main.py`, and `step4_Speed_Cluster/step4_Speed-Cluster_docs/04_augmentationGSS_IMP_2.md`
  (grepped first, then read narrow ranges).
- Also read `manuscript/draft_S2_framework.md` (full, 417 lines) to check for overlap; found it
  describes a DIFFERENT, earlier donor step (census-to-diary matching, section 2.4, demographic
  four-level fallback) that this draft explicitly distinguishes from the day-type completion donor-draw
  covered here.

## Verified
Full number trace table with file:line citations is in the draft itself
(`manuscript/draft_SI_schedule_completion.md`, "Number trace table" section, 17 rows). Every row was
read directly from its cited source in this task; the two peer-produced findings reused (T24's
historic-cycle donor-pool scope, T21's sampling-pool numbers) were re-checked against their own primary
sources before citing (T24's citations verified verbatim against `08_gen_cycle_schedules.py`; T21's
numbers are quoted from that task's own completed Ledger entry, not re-run here, since this task has no
cluster access).

## Decisions
- Numbered the new SI sections S.5-S.9, continuing the sibling part's S.1-S.4, on the assumption the
  two parts sit in the same appendix in sequence. Not confirmed with the author; flagged for the
  collector to renumber if wrong.
- Explicitly separated this draft's donor-draw (day-type completion) from `draft_S2_framework.md`
  section 2.4's census-to-diary matching, since both are random draws from a diary pool and are easy to
  conflate; this distinction was not asked for in the task content list but follows directly from
  reading both sources.
- Kept the 2022 genuine at-home rates and copy-day method-history numbers (69.77/72.95/76.57%, 74.76%,
  77,313 households, 72.00%) as method-history facts (already reflected in the archived manuscript's own
  "-2.76 pp" sentence), not as a current-campaign result needing rebuild under ruling (b). Flagged the
  pre-refresh person-count mismatch (285,419 vs current 285,367, a 0.02% difference) in the trace
  table's Notes rather than treating it as a blocker.
- Did not estimate the S.8 per-group audit; wrote it as `[VALUE PENDING: ...]` since no source produces
  it and this task has no cluster access to produce it.
- Found a gap in `draft_S2_framework.md` section 2.8 (sampling procedure): it omits that the sampling
  candidate pool is filtered by a schedule sanity check before the 50-household draw, which is the
  entire basis of the new S.8 caveat. Did not edit that file (out of this task's scope, one file only);
  flagged in the draft's own Next section instead.

## Next
Collector/manager to: (1) confirm or renumber the S.5-S.9 section numbering against the sibling part's
actual placement; (2) add the missing sanity-check clause to `draft_S2_framework.md` section 2.8
(`integration.py:219-266,432-438`); (3) commission the pending 24-group sanity-check drop-count audit
if needed beyond the one group already measured; (4) review whether the draft's opening paragraph
distinguishing the two different "donor draws" (census-to-diary matching vs. day-type completion) reads
clearly on its own.

## WHAT I DID NOT VERIFY
Full list is in the draft's own "WHAT I DID NOT VERIFY" section. Headline items: did not re-run the
sampling-pool caveat's numbers from raw logs (no cluster access, read one level removed from the raw
`.out` file via an already-collected task Ledger); did not measure the sanity-check drop counts in any
group beyond the one audited; did not verify the 2022 genuine at-home percentages against a rebuilt run
of the current (post-refresh) person set; did not trace whether `write_8760_schedule_csv` or
`create_compact_schedule` (both cited for the annual-assembly mechanism) is the one actually used to
produce the files EnergyPlus reads for the reported campaign.

## Status: DONE
Draft written to `manuscript/draft_SI_schedule_completion.md` (329 lines): sections S.5-S.9 plus a
17-row number trace table and full Ledger/Verified/Decisions/Next/WHAT I DID NOT VERIFY sections. No
cluster access used. No em/en dashes, no banned jargon labels, "limitation" used throughout (checked by
grep before finishing). Token budget not exceeded (~120k used this session).

## Manager review (2026-09-15, manager, Opus)

**Verdict: ACCEPTED with four manager corrections applied.** `manuscript/draft_SI_schedule_completion.md`
exists, sections S.5 to S.9 plus a number trace table. Strong work: the agent found two things the task
doc did not ask for and both were right.

**Re-checked at source (manager, independently of the agent):**
- `2J_docs_occ_nTemp/07_aug_to_bem.py:148-180` read in full. Confirms every claim of S.7: seed 42
  (`np.random.default_rng(42)`), the pools (`wd_pool = DDAY_STRATA == 1`, `we_pool = isin([2,3])`, so
  Saturday and Sunday pooled into one donor pool), no demographic narrowing, only the activity and
  at-home columns overwritten, the per-member draw, and the docstring's own "copy-day biased it
  -2.76 pp" plus its synthetic-co-presence limitation. The draft's S.7 is an accurate plain-English
  rendering of this function.
- `2J_docs_occ_nTemp/07_aug_to_bem.py:34` - `DAYTYPE = {1:"Weekday",2:"Weekend",3:"Weekend"}`. Confirmed.
- `2J_docs_occ_nTemp/07_bemIntegrationGSS.md:60-68` - the two-day-type reduction, described there as a
  deliberate deviation from the planned three-type output. Confirmed.
- `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-438` - the S.8 caveat numbers (103 and 104 dropped,
  paired pool 16,326, published 16,208, difference 320, the positive control reproducing 130322/80058
  and the new draw 130228/79252). Confirmed, and consistent with the T37 limitations draft.

**Ruling (a) check: PASS.** This part does not touch the weekend-ceiling result at all; it correctly
points at the sibling SI part for it and never claims the weekend passed.

**Ruling (b) check: FAILED as written, now fixed.** The agent argued three sets of numbers were method
history rather than campaign results and kept them. The manager disagrees on all three and has replaced
them with marked PENDING placeholders:
1. The 2022 at-home rates by day type (69.77 / 72.95 / 76.57 %, pooled weekend 74.76 %, lift 4.99 pp).
   These were read from a Step-4 working note describing a person file of 285,419, and
   `07_bemIntegrationGSS.md:30` records the current file at 285,367 after the 2026-07-09 refresh. The
   draft presented them in S.6 as a property of the calibrated 2022 stock, that is, as a current
   descriptive statistic, not as history. Under the ruling they are re-derived or dropped.
2. The 2030 Saturday and Sunday rates (79.15 % and 81.48 %, the about 2.3 pp lost by pooling). These
   come from the joint-raked 2030 diary file that the D1 build replaced. The current 2030 target is
   `clamp(stock_rate + 8 x pre_slope, 0, 1)`, a different construction, so these are an old-build
   number by the plainest reading of the ruling.
3. The 77,313 weekday-only household count behind the copy-day comparison, same pre-refresh file.
   **Kept**: the 2.76-point copy-day bias itself, because it is stated in the current completion step's
   own code at `07_aug_to_bem.py:151-153` as the reason the method was replaced, and the S.8
   sampling-pool figures, because they are a rebuild-verification finding produced during this revision.
   The trace-table header now records this correction in full.

**Manager corrections applied.**
- S.6 paragraph 1: the three 2022 stratum rates replaced by a PENDING placeholder.
- S.6 paragraph 2: the 2030 Saturday and Sunday split replaced by a PENDING placeholder; the
  qualitative statement that the pooling discards the calibrated difference is kept and strengthened.
- S.7 method history: rewritten to carry the 2.76-point bias and the reason for it, without the
  pre-refresh per-stratum rates.
- Header line: the internal task label removed from the prose.
Three trace-table rows re-marked PENDING accordingly.

**The agent's two unrequested findings were both correct and both acted on.**
1. **Plan §5 item 5 is settled and is a real limitation.** The agent's S.6 establishes, from the code,
   that Saturday and Sunday are pooled into one weekend pattern at the building-model interface while
   the diary model keeps three day types apart. That is exactly the open item the T37 collection
   deferred. A tenth limitation has been added to `manuscript/draft_S7_limitations.md` ("Saturday and
   Sunday are simulated as one day"), with its own trace row, no number quoted because the size is
   PENDING. Plan §5 item 5 is now covered and needs no separate handling in step 13.
2. **The framework draft's section 2.8 was incomplete.** It described the candidate pool as every
   household identifier present in the schedule files, which omits the plausibility filter that is the
   entire basis of the S.8 caveat. One clause added to `manuscript/draft_S2_framework.md:246-247` in
   plain words, pointing to the supplementary material for what it implies. The agent was right not to
   edit that file itself.

**Prose-hygiene check: PASS.** Machine check on the prose sections only (scratchpad `chk38.py`): zero
em or en dashes, zero curly quotes, zero banned labels, zero T-numbers after the header fix, the word
"failure" absent, three marked PENDING placeholders and nothing estimated.

**Open items carried forward, none a defect:**
- The SI section numbering S.5 to S.9 assumes this part follows the model-selection part. Confirm the
  appendix order at assembly (step 13) and renumber if it differs.
- The 24-group drop-count audit behind S.8's PENDING row is commissioned only if the response to
  reviewers needs a number beyond the one audited cell. Not needed for the current argument.
- The agent did not establish which of the two calendar-expansion code paths the campaign actually
  uses (`create_compact_schedule` versus `write_8760_schedule_csv`). Both implement the same weekday
  and weekend rule so no claim in the draft turns on it, but step 13 should name the one in use.

Status: DONE. Draft is usable as the second SI part.

