# T37 — WP10: main-text limitations section draft, every claim traced to source

Task doc and implementation state in one file. Written by the manager 2026-09-15 (plan log (ba)).
Agent: Sonnet, fresh session. **Local reading and writing only. No cluster. No cluster commands at all.**

## Aim
Write one draft of the manuscript's limitations section for the Applied Energy resubmission:
`rejection revision/manuscript/draft_S7_limitations.md`. The rejection turned partly on limitations being
scattered or soft, so this section states each one plainly, in the author's own voice, with no defensiveness
and no hedging. **Every limitation must already be established in the project record**; you invent nothing and
you soften nothing.

## The limitations to cover (each one is already decided; your job is the prose and the trace)
1. **The before/after comparison is not household-paired across stocks.** The rebuilt schedules change which
   households pass the engine's sanity check, so the pool differs from the published one (16,326 vs 16,208 for
   one cell, 320 households) and the same seed draws a different sample. Source: plan log entry (ak) and
   `impl/2026-09-15_T21_wp1_step8_step9_rerun.md` ledger.
2. **One envelope only.** No source prints a U-value or SHGC for the dominant glazing type, so the existing-stock
   envelope variant was not built and is not reported. Source: plan log entry (aq) and
   `impl/2026-09-15_T31_wp7_existing_stock_envelope.md`.
3. **The synthesized weekend days.** Apply the author ruling exactly as `manuscript/draft_SI_model_selection.md`
   S.3 now states it: one distance ceiling of 0.10 for every day type, the weekend does not meet it, the later
   widening to 0.20 is not used, the gap sits in the synthesized rows (observed-only 0.036 and 0.040 against
   synthetic-only 0.138 to 0.175), and two weekend up-weightings moved the score by about 0.005. Main text gets
   three or four plain sentences and points to the SI. **The main text must never say the weekend passed.**
4. **Validator check 3.5.** The frozen 2022 stock scores 75.04 % against a 72.3 % band that was not moved.
   Source: plan log entry (aa) and the T18c task doc.
5. **The 2030 build is a scenario, not a forecast.** State what D1 holds fixed. Source: the WP1 spec
   `impl/2026-09-15_WP1_step2_retargeting_spec.md` and `impl/2026-09-15_T20_wp1_d1_2030_build.md`.
6. **Scope**: six cities, four dwelling archetypes, one country's time-use survey; no measured whole-building
   energy for validation. Confirm the exact archetype and city lists from §0 of the manager prompt before writing.
7. Anything the plan's §9 closure boxes already mark as a stated limitation and that is not in the list above:
   add it, and say in the Ledger where you found it.

## Rules
- Prose says **limitation**, never failure, never "unfortunately", never "we were unable to". A limitation is
  stated, bounded, and followed by what it does and does not affect in the results.
- Plain words. Labels banned in prose: J3, True-Future-Test, frozen frame, Tier-1/2/3, FailSafe, Step-8, Step-9,
  occACT, gate, PASS/WARN/INFO, Nb-f, T-numbers. Say "the chosen model", "the rebuilt stock", "the check".
- **Numbers must be re-read from the source named above**, not copied from this task doc. If a number in this
  task doc disagrees with its source, the source wins and you record both in the trace table.
- **Ruling (b) applies**: any number that comes from the old simulation campaign is not used. If a limitation
  needs a number the rebuilt runs have not produced yet, write the sentence with a clearly marked
  `[VALUE PENDING: <what is needed, which run produces it>]` placeholder. Do not quote an old-campaign number.
- No em dashes, no en dashes. Write only `manuscript/draft_S7_limitations.md` and this file. Do not edit the plan,
  the archive, the code, other task docs, or any submission file.
- Never run `mkdir`, `find`, `du`, `md5sum`, `cp`, or any python on the Speed login node. This task does not
  touch the cluster at all. Never open a multi-MB file whole: use `grep -n`, `head`, `wc -l`, offset/limit reads.
- End with a **claim trace table**: claim · the plain sentence that carries it · source file:line · matches the
  source (yes / no, give both) · PENDING if it needs a rebuilt-run number.
- Append to Ledger and Verified as you go. End the turn when the draft exists; do not wait for anything.

## Ledger
- No cluster jobs. Local-only session. Read (grep + offset reads, nothing multi-MB opened whole):
  `00_REVISION_PLAN.md` (entries aa, ak, aq; sections S5, S9, S10), `2J_manager_prompt_RESUME_AE_resubmission.md`
  (§0 engine facts), `impl/2026-09-15_T21_wp1_step8_step9_rerun.md`, `impl/2026-09-15_T31_wp7_existing_stock_envelope.md`,
  `impl/2026-09-15_T18c_wp1_frame_v2.md`, `impl/2026-09-15_WP1_step2_retargeting_spec.md`,
  `impl/2026-09-15_T20_wp1_d1_2030_build.md`, `manuscript/draft_SI_model_selection.md` (S.3),
  `impl/2026-09-15_T09_wp5_sim_vs_measured_toronto.md`. Wrote `manuscript/draft_S7_limitations.md` (new file).
  Status: DONE.

## Verified
- T21 household-pool numbers (`impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-438`): rebuilt paired pool
  16,326 vs published paired pool 16,208, symmetric difference 320, one cell (SingleD x Montreal). Matches
  task doc exactly.
- T31 envelope (`impl/2026-09-15_T31_wp7_existing_stock_envelope.md:408-412,417`): dominant glazing Swan
  code 200, double glazed clear 13mm air, 74.0% of single-detached window area; window U/SHGC NOT FOUND;
  rule 8 fires; WP7.3 not run; one-envelope limitation stated in the source doc's own words.
- T18c validator check 3.5 (`impl/2026-09-15_T18c_wp1_frame_v2.md:56-58,61`): 75.04% vs 72.3% anchor, delta
  2.74pp, band 2pp, FAIL. Task doc gives 75.04%/72.3%/band but not the 2.74pp delta; added from source
  (source wins, both recorded in the draft's trace table).
- SI S.3 weekend numbers (`manuscript/draft_SI_model_selection.md:95-128`): ceiling 0.10 all day types;
  weekday 0.0619/0.0630 pass; weekend 0.1817/0.1843 (held-out) and 0.1637/0.1618 (backcast) fail; observed-
  only weekend 0.036 Sat / 0.040 Sun; synthesized rows 0.138-0.175; up-weighting twice moved score ~0.005;
  0.20 ceiling disclosed but unused. All match task doc exactly.
- 2030 D1 formula, confirmed identically in two independent files: `target[s,t] = clamp(stock_rate[s,t] +
  8 x pre_slope[s,t], 0, 1)` (`impl/2026-09-15_WP1_step2_retargeting_spec.md` §3; `impl/2026-09-15_T20_wp1_d1_2030_build.md:9-18`).
  Same stock persons/diaries as 2022; pre_slope from real 2005/2010/2015 respondents.
- Scope facts (`2J_manager_prompt_RESUME_AE_resubmission.md:59-61`): archetypes SingleD, OtherDwelling,
  MidRise, HighRise; cities Toronto_5A, Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B, Winnipeg_7A —
  four archetypes, six cities, matches task doc's "six cities, four dwelling archetypes."
- Measured-check scope (`impl/2026-09-15_T09_wp5_sim_vs_measured_toronto.md:11-13,38-41,150,182-186`):
  comparison is `Electricity:Facility` only, Toronto + Ontario, shoulder-season weekdays (n_days=82); not
  a whole-building energy measurement, not available for the other five cities.
- Item 7 (additional decided limitations): the literal §9 checklist (`00_REVISION_PLAN.md:565-580`) has
  only meta rows, no itemised limitations. Found the itemised list instead at §5 "Weaknesses the reviewers
  did not raise" (`:470-483`): TMY weather (item 1), one climate-zone envelope for all cities (item 2, folded
  into the main envelope paragraph), Census-GSS conditional independence (item 3), metabolic heat channel
  not independently calibrated (item 4), weekend pooled into one day type (item 5, NOT included, see WHAT
  I DID NOT VERIFY). This same §5 list is cross-referenced as the standing limitations set by the Wave-5
  audit prompt at `:658-659`.

## Decisions
- Used §5 (`00_REVISION_PLAN.md:470-483`), not §9, as the source for task item 7, since §9 itself contains
  no itemised limitations. Recorded this substitution rather than leaving item 7 blank or silently treating
  §5 as "§9."
- Folded S5 item 2 (one climate-zone envelope for all six cities) into the same paragraph as limitation #2
  (existing-stock envelope not built), since both trace to the same T31 closure; given a "Partial" match in
  the draft's trace table rather than a separate paragraph, to avoid diluting the primary WP7.3 claim.
- Did not include S5 item 5 (weekend pooled into one day type; hourly reporting) as its own sentence: it is
  a distinct claim from the already-covered synthesized-weekend limitation and needs its own source check
  outside this task's five named sources.
- No `[VALUE PENDING]` placeholders needed: every number traces either to a rebuilt-run source file (ruling
  (b) satisfied) or to pre-rebuild plan/manager-prompt facts (city/archetype list, §5 items), never to an
  old-campaign number.

## Next
- Draft is complete at `manuscript/draft_S7_limitations.md` with a full claim-trace table. Manager to fold
  into the assembled manuscript; re-run T-AUDIT provenance check against the same source files at final
  assembly. No further action owed by this task.

## WHAT I DID NOT VERIFY
- This task doc's own header cites "plan log (ba)" as the commissioning entry; grep of `00_REVISION_PLAN.md`
  found no entry literally labelled "(ba)" (log ran (aa) through (az) at read time). Did not chase further;
  does not change any limitation's content. Flagging for the manager.
- S5 item 5 ("weekend pooled into one day type; hourly reporting") read but not traced further or included
  in the draft; may need its own sentence and citation as a separate, sixth reviewer-unraised limitation.
- Did not independently re-verify T18c's or T21's upstream numbers (did not re-run the validator or the
  engine's sanity check); took the task docs' own Verified/Ledger sections as the source, per this task's
  local-reading-only scope.
- Did not check `draft_S7_limitations.md` for wording or number conflicts against other already-drafted
  sections (`draft_S2_framework.md`, the rest of `draft_SI_model_selection.md`); out of this task's scope.
- Did not verify Applied Energy's house-style length convention for a limitations subsection; wrote to the
  content specified, not to an external length rule.

## Manager review (2026-09-15, manager, Opus)

**Verdict: ACCEPTED with one correction applied by the manager.** `manuscript/draft_S7_limitations.md`
exists, 9 limitations in 7 paragraphs, followed by a claim trace table.

**Re-checked at source (manager, independently of the agent):**
- `impl/2026-09-15_T18c_wp1_frame_v2.md:56-58,61` - "75.04% vs 72.3% anchor, delta 2.74 pp, band 2 pp"
  and "real-2022 donors 74.31% unweighted (n=159,295; weighted 72.31%)". Draft matches. The agent's
  addition of the 2.74 pp gap (absent from the task doc) is correct and is the source's own number.
- `impl/2026-09-15_T21_wp1_step8_step9_rerun.md:429-438` - new paired pool 16,326, published paired
  pool 16,208, symmetric difference 320, cell `SingleD__Montreal_6A`. Draft matches, including the
  cell identification ("single-detached houses in the Montreal region").
- `00_REVISION_PLAN.md:470-483` (S5) - items 1, 3, 4 used as the three extra limitations; correct.
- `manuscript/draft_SI_model_selection.md:95-128` (S.3) - every weekend number in the draft matches
  the SI part verbatim (ceiling 0.10 for every day type; weekday 0.0619/0.0630; weekend 0.1817/0.1843
  held-out and 0.1637/0.1618 backcast; observed-only 0.036/0.040; synthesized 0.138-0.175; about 0.005
  from two up-weightings; the 0.20 widening disclosed and used nowhere).

**Ruling (a) check: PASS.** The main-text prose never says the weekend passed. It says the weekend
"does not meet this ceiling", names one ceiling of 0.10 for every day type, and states that no weekend
result should be read as having passed a ceiling set before the fact.

**Ruling (b) check: PASS.** No old-campaign or old-build number appears. Every number traces to a
rebuilt-run document (T18c frame v2, T21 rerun) or to the model-selection SI, none to the published
campaign. No PENDING placeholder was needed. One watch item below.

**Prose-hygiene check: PASS.** Machine check on the prose section only (scratchpad `chk37.py`): zero
em dashes, zero en dashes, zero curly quotes, zero banned labels (J3, True-Future-Test, frozen frame,
Tier-n, FailSafe, Step-8, Step-9, occACT, gate, PASS/WARN/FAIL, Nb-f), zero T-numbers. The word
"failure" does not appear; "limitation" is used throughout. Banned tokens appear only in the trace
table and Ledger, which are manager-facing scaffolding and are stripped at assembly.

**Correction applied by the manager.** The opening sentence read "This work has six limitations" while
the section lists six plus a further three, nine in total. Rewritten to: "This work has nine
limitations. The first six bear directly on the results reported above; the last three are disclosed
here although no reviewer raised them." No other wording touched.

**The agent's (ba) flag is resolved, no action needed.** Plan log entry (ba) does exist, at
`00_REVISION_PLAN.md:1064`. The agent grepped the plan before the manager's append landed. The agent
was right to record it rather than assume.

**Two open items carried forward (not defects in this draft):**
1. S5 item 5 ("weekend pooled into one day-type; hourly reporting") is the one S5 item not covered.
   The agent correctly declined to write it without its own source check. It is deferred to the T38
   collection, because T38 documents the day-type strata and the reduction to the resolution
   EnergyPlus reads, which is exactly where this claim is either true or not. If T38 shows Saturday and
   Sunday are carried separately into the schedules, the S5 item is stale and gets struck; if they are
   pooled, a tenth sentence is added here. Recorded in the manager prompt, step 13.
2. The scope paragraph describes the measured-data check as Toronto and Ontario electricity on
   shoulder-season weekdays, sourced from the T09 task doc. T09 is on the Wave 4 re-derivation list.
   No T09 *number* is quoted in the prose, only the description of what was compared, so ruling (b) is
   not breached; but this paragraph is re-read once T09 is re-derived. Recorded in the manager prompt,
   step 8.

Status: DONE. Draft is usable as the S7 base for the WP10 rewrite.

