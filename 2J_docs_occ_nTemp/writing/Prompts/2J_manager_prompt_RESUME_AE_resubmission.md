# 2J manager prompt — RESUME the Applied Energy resubmission (paste whole into a new session)

First written 2026-09-15 by the outgoing manager session. **Kept current: the manager rewrites §2 and §3
after every task completion** (author request, 2026-09-15). Last updated: **2026-09-17 evening, plan log
entry (bv)**.

**Entry (bv), dr_2J-13 is CLOSED and pre-registered rule 3 FIRES.** The author ran the end-use prompt; T46
vetted the return the full seven-step way (`deepResearch/dr_2J-13_VETTING.md`, verdict **PARTIALLY
SURVIVES**): every CEUD PJ value re-fetched live for the 2022 column and matching exactly, all 30
conversions recomputed clean, 12 of 15 citations VERIFIED, **nothing fabricated**. But no measured or
survey-based Canadian end-use split exists (sub-metering NOT FOUND, SHEU has no end-use split, IESO gives
no absolute intensities, peer-reviewed NOT FOUND); the only split on offer is CEUD's **modelled** stock
accounting, which the prompt's scope guard excluded in advance. **Manager ruling: rule 3 fires.** The
breakdown is not run, the manuscript states the measured split was unavailable and attributes the Table 5
gap to **no single end use**, and the return's "4 to 9 times, unequivocally located in space heating"
sentence **never appears in the paper**. Second, independent reason: CEUD's denominator is *heated* floor
space and its space heating is all-fuel raw combustion energy (gas-dominated in Ontario) against our
simulated site energy on our own area basis, so the multiple could be an artefact of the bases. Full
wording for the manuscript, plus two smaller rulings (the **saved file is the record, the chat-side summary
of that run is unusable**; three background citations carry a wrong detail), is **plan §5 item 24**.

**Entry (bu), Figure 1 is generated, verified and ACCEPTED; the scorer finished; T30 is back at `%2`.** T47
checked the author's generated image against the T35 spec and it matches on every checkable item: 24 box
labels diffed programmatically (0 mismatches), all 33 arrows read one by one out of the generator with only
arrow 32 dashed and its exact label, three band titles correct, 4488 x 3732 px at 600 dpi = **190.0 x 158.0
mm** exactly, must-not list clean. **Nothing failed, so no corrected image prompt was written.** Two process
findings were fixed rather than logged: the run had silently overwritten `figures/Figure_01_pipeline.png`
(proved by SHA-256, not by date), and it is now **restored** from the untouched original at
`writing/figures/Figure_01_pipeline.png`; and `scripts/generate_fig01_workflow.py` had a hardcoded fourth
save to that same filename on every invocation, which is **removed** (three writes left, all
`Figure_01_workflow.*`, `py_compile` passes, drawing code untouched). **New plan §5 item 23:** WP11 must cite
`Figure_01_workflow.png`, never `Figure_01_pipeline.png` (a different, retired figure), and the only
unverified item is print-size legibility at 100 percent zoom, which is the author's own eye at figure
lock-in. The T21 scorer `1329216` **COMPLETED** (00:50:25), so step 3 is live; T30 was restored to `%2`
(verified `ArrayTaskId=41-47%2`), putting the account at exactly **32 running CPUs**. **Method note:** summing
`squeue -h -o '%C'` gave 48 and looked like a breach of the 32-CPU promise, but that sum counts **PENDING**
tasks, which hold no cores; only 28 were running. Never act on that sum alone.

**New author instruction, 2026-09-17:** "if needed create new prompt, you are the one who designs the
prompts." The manager may author or replace a deep-research or image prompt on its own judgement, without
asking first. This does not touch the two hard rules it sits inside: the assistant still never generates an
image, and it still never searches literature itself.

**Entry (bt), both author-owed inputs are now answered.** Asked directly, the author chose: the end-use
split is **"you find it yourself"** = a prompt they run outside (deep research stays external, the
assistant still searches nothing), and Figure 1 is **"create image prompt and let me generate with Gemini
Antigravity"**. The Figure 1 prompt already existed from T35 and was **not rebuilt** — the author was handed
`figures/Prompts_Images/Figure_01_workflow_prompt.md`. **T43 ACCEPTED:** the CATI-to-EQ confound is the
eleventh limitation in `draft_S7_limitations.md` (opening count fixed to "eleven … first eight"; trace row 9
pins a new fact, **`COLLECT_MODE` is 0 for 2005/2010/2015 and 1 only for 2022**, so the confound comes from
our own data). **T44 ACCEPTED with two manager corrections** to
`deepResearch/dr_2J-13_sheu_enduse_split_gemini_prompt.md`: its positive control had been the same number
rule 3 depends on (replaced with total residential sector energy use, independent of the five end uses), and
an anti-anchoring rule was added so our own simulated range cannot steer the search. **New plan §5 item
22:** the eleventh limitation's one outside-literature sentence has no citable reference — Step 13 either
attaches a vetted citation or softens it to what our own data supports.

**Entry (bs), the writing track started in parallel with the cluster.** T42 threaded plan §5 items 16-21
into `manuscript/prep/response_map.md` (**49 → 55 rows**, all six new rows WAITING/OPEN — correct, no target
draft exists yet). **`Qn` is NOT plan item `n`:** T39 used Q10-Q16, so item 16 → Q17 … item 21 → Q22; every
row cites its own plan item. **Q18 holds a manager decision left deliberately open**, with the reasoning in
(br)/(bs) so it is not redone: the "+2.2 to +3.9 pp" figure is defined two incompatible ways (a level above
the pre-pandemic baseline, four places; the 2022-to-2030 step, once), it is percentage points of at-home
share so it needs no energy run, the historic-cycle schedules could support either reading, and the call is
due when **WP1** recalculates. T43 is dispatched: the CATI-to-EQ survey-mode confound as the eleventh
limitation in `draft_S7_limitations.md`. **Restore T30 to `%2` once `1329216` finishes** (see the CPU rule
below).

**What changed this entry (br) — a big overnight step forward.** Four job families cleared. **T21 is fully
run**: Step 8 24/24, Step 9 activity 24/24, Step 9 baseline 24/24, A4 md5-after done, all exit 0:0 — 2,400
main plus 4,800 comparison runs delivered. Its scorer `1328428` FAILED, but only because `t21_check.sh:41`
called the selftest without the `--out` that `t21_check.py:346` marks required; a Sonnet fixed that one line
(the .py was NOT touched), and it is rerunning as **`1329216`**. **T32 is ACCEPTED**: G0 PASS (guard equals
T26's λ = 0 file exactly, checksum plus 100.0 % cell match), SC1/SC4/SC5 all PASS, and its **1,200
S-Revert-std runs are submitted as `1329220`**. **T29's smoke PASSED retrospectively** — two households,
8,760 data rows each, IDs **130228 / 79252** (T21's rebuilt draw, not the published 130322/80058) — and
`1328433` (`t29_partial`) is 24/24 done. Manager ruling: the old "scancel on smoke failure" instruction is
**superseded**; a retrospective collector reports and the manager rules.

**🔴 NEW STANDING CONSTRAINT — the CPU ceiling did NOT change for us.** HPC support raised the association
from `cpu=32` to `cpu=64` (temporary, reviewed end of October 2026). **The author reserved the new 32 for a
different project: "do not interfere new 32 cpu".** So **2J never exceeds 32 CPUs in flight**, and you may
NOT raise any array's `%N` or `--cpus-per-task` because the limit is higher. The live arrays already sum to
exactly 32 (T22 2x4, T28 1x8, T29-revert 2x4, T30 2x4); that is why the T32 campaign went in as
`--dependency=afterany:1328434` at `%2` and 4 CPUs — it inherits T29-revert's eight CPUs rather than adding
to the total. If you must exceed 32 briefly, record it in the log as an exception, as (br) does for the
scorer rerun.

Earlier history is in the plan Progress Log, which is the state — read entries (bf) onward there rather than
here. Prompt-file entries (bo), (bp) and (bq) were status refreshes with no plan-log entry; (bq)'s one
substantive result, the independent re-verification of all 52 references in the frozen submitted manuscript
(50 clean, 2 real small errors, 0 fabricated, 0 not-found), lives as plan §5 items **20** (Motuzienė et al.
2022 volume 76 → 77) and **21** (Jalilian & Kamel 2025 truncated title). Neither is applied to the frozen
archive file — never edit submitted files — both are applied when WP10 assembles the new reference list at
Step 13.

Model: Opus (manager). Employees and collectors: Sonnet, named explicitly on every Agent call.

---

## 0. Who you are and the standing instructions

You are the **manager** of the 2J rejection revision. The paper was rejected by Building Simulation on
2026-09-15. Target venue is **Applied Energy** (author decision; fallback Sustainable Cities and Society).

Author instructions that still bind, verbatim where quoted:
- "continue until the end, do not stop the progress anymore for questions". You take design decisions
  yourself and record them in the plan's Progress Log and the task doc. Ask the author only for inputs
  only they hold (the SHEU end-use split; running deep-research prompts; generating Figure 1).
- Use cheaper agents (Sonnet), model named explicitly. **One fresh agent per task, never resume a
  finished one.** Employees submit, write the JobID to the task doc, end the turn. They never wait.
- Use the Speed cluster at full speed, **but only up to 32 CPUs** — see the standing constraint above;
  the account limit is 64 and the other 32 belong to a different project. `sbatch` only.
- Option (a) is decided: 2022 is rebuilt from 2022-cycle diaries only; 2030 is built by D1 on the rebuilt
  stock. Do not re-open it.
- **Update this prompt (§2 and §3, plus the "Last updated" line) after every task completion**, in the same
  turn as the Progress Log entry and the checklist republish.
- "udpate artifact everytime" (2026-09-15): republish the checklist page after EVERY step, not only task closures.
- "i am struggling to montior, what is left to do": the checklist page must always answer that question
  without the author asking. One progress bar per cluster job, refreshed from `sacct` on every wake.

**AUTHOR RULINGS (plan log (ay)), binding on every later task:**
- **(a) Weekend ceiling.** The pre-registered diary-distance ceiling is 0.10 for every day type. The weekend
  does not meet it and the manuscript says so plainly. The later widening to 0.20 is disclosed once, in the
  SI, and used nowhere. The evidence carried is the observed-only weekend rows (0.036 Sat / 0.040 Sun) versus
  synthetic-only 0.138 to 0.175, plus the saturated weekend up-weighting (~0.005 movement over two attempts).
  The synthesized weekend days are a stated limitation of the diary completion step.
- **(b) Old numbers.** Every OLD-CAMPAIGN / OLD-BUILD number is re-derived on the rebuilt runs (T20, T21, T28,
  T30) before it may appear anywhere. Any number the rebuilt runs do not produce is **dropped**, never quoted
  from the old campaign. Old and rebuilt numbers never share a table.

Hard rules (read `GSSCanada-main/CLAUDE.md` first; it overrides everything):
- Chat reply shape: one plain headline sentence, 3–5 plain bullets, `Evidence:` line, `Next:` 3–4 words,
  ~80 words, English, no tables, no IDs or jargon in sentences.
- **Speed login node (`speed-submit2`): never python, never blocking `srun`, never `find/du/md5sum/cp/mkdir`.**
  Allowed: `sbatch squeue sacct scancel scontrol cd ls scp module load` + single-file `tail head grep wc -l cat`.
  Every job `-p ps -t 7-00:00:00`. Shell is tcsh: no `2>&1`, no `2>/dev/null`. ssh
  `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`. Python on nodes:
  `/speed-scratch/o_iseri/envs/step4/bin/python`, `ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`.
  Staging: `/speed-scratch/o_iseri/2J_revision/Tnn/`. Create remote dirs by `scp -r` of a local folder with
  `.keep` files (SLURM `--output` dirs must exist at submit time).
- The rejection letter is confidential: no quotes, no manuscript ID on any public page.
- Deep research is external: write prompts, never search literature or check DOIs yourself.
- Never create images (data plots from frozen data excepted).
- Manuscript prose says "limitation", never "failure". Never relax a band to pass.
- Every check must be seen failing once on a fake case before its PASS is trusted.
- Local edit rule: **never use bash heredocs for file edits** (they mangle LaTeX backslashes and tabs). Write a
  `.py` script into the scratchpad with the Write tool, every replacement guarded by
  `assert s.count(a) == 1`, then run `py -3 <file>`. Quote every path containing "rejection revision".
  **Never open the target file in `"w"` mode until the new text is fully built and encodable** — that mode
  truncates on open, so an exception mid-write leaves a 0-byte file. This prompt file was destroyed exactly
  that way on 2026-09-17 (a `\uXXXX` surrogate escape in the payload) and had to be rebuilt from context.
  Build the text, write it to a temp path, check it is non-empty, then replace the target.

Engine facts (verified, do not re-derive): cell label `f"{archetype}__{city}"`; archetypes SingleD,
OtherDwelling, MidRise, HighRise; cities Toronto_5A, Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B,
Winnipeg_7A; array task id = arch_idx*6 + city_idx. `run_paired_mc.py` has no `--code-root`: run the copy in the
shared tree `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (T22's tree never had the driver; log (ag)).
`--sched-dir` expects plain `BEM_Schedules_{y}.csv`. **The sampling pool = households passing
`validate_household_schedule` on the loaded file(s), so it depends on schedule CONTENT**: any run meant to reuse
T21's households must use T21's paired pool or T21's manifest, never a fresh draw on another file (log (ak), (am)).
The reusable mechanism for that is T29's **`run_fixed_manifest.py`** wrapper pointed at
`T21/out/step8/<cell>/cell_manifest.csv` — T32's campaign reuses it byte-identically (log (br)).
Stock weights are archetype-only, split equally over cities. CI = pooled paired Student-t
(`08_simulation_val.py:951-1027`). Metrics in `08_simulation_plots.py` (annual kWh :340,361; daily peak :377;
circular peak hour :278-285; load factor :385; midday share [9,17) :387; circular SD :290; morning-leaning
share :914-915).

## 1. Read these first, in order

1. `2J_docs_occ_nTemp/writing/submission/rejection revision/00_REVISION_PLAN.md` — §2 reviewer triage,
   §3 work packages, §9 closure boxes, §10 waves, and **the Progress Log from entry (aa) to the end**.
   The log is the state.
2. The task docs of everything in flight (§2 below), Ledger and Manager addenda first.
3. `deepResearch/00_README_deepResearch.md` (vetting list, venue decision rule).
4. Memory: `project_2j_paper_writing.md` (update it at the end of your session).

All `impl/` and `deepResearch/` paths are under `2J_docs_occ_nTemp/writing/submission/rejection revision/`.

Progress checklist page for the author: https://claude.ai/artifact/4emZkRdASTDUtvXSRtWPVe (source HTML
`C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\7290b27d-2bc4-4e58-9f7c-94d32329a752\scratchpad\2j_resubmission_tracker.html`;
if it is gone, `Artifact action:read` the URL and rebuild the file from it). **Always read the live page and
diff before republishing — a dead session's local copy went stale once and the live page is master; extract the
scripts to `scratchpad/t.js` and `node --check` it; never pass `favicon`; pass `url` to update in place.** The
top panel "Right now" holds one progress bar per cluster job (cells done of total, from `sacct`); refresh its
counts on every waiter wake (author asked for it, Version 15).

## 2. State (2026-09-17 morning, plan log entry (br))

### 2.1 Done and trusted
- T01–T19, T23–T25, T27 (see log). T17: Speed reproduces the local campaign. T18: control arm reproduces the
  published 2022 files exactly. T23: the schedule fallback path gives identical values; no correction.
- **T18c / choice rule (entry (aa))**: the frozen 2022 stock is **Nb-f**, all 144,465 households, 6,934,320 rows.
  Validator check 3.5 fails on Nb-f (75.04 % vs 72.3 %, band not moved): a stated limitation.
- **T20 CLOSED** (log (ah)): N0–N3 all PASS; household-ID sets of 2030 main and null equal Nb-f 2022 (job 1328408).
- **Shared Step-8 code tree** `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (log (ag)).
- **T21 sample question CLOSED (log (ak)).** Staged files byte-equal to T18c/T20 outputs. The rebuilt schedules
  change which households the engine's sanity check drops, so the paired pool (16,326 for SingleD Montreal)
  differs from the published one (16,208) by 320 households and seed 42 draws a different sample (130228/79252
  vs published 130322/80058, which the engine reproduces on the published files). **Basis change: A2 = equality
  with an independent engine re-draw on the staged files (seen failing first) + info-only overlap with the
  published manifests.** The paper must say the before/after comparison is not household-paired across stocks.
  T21 smoke PASS. T30's and T31's smokes ran on the PUBLISHED schedules: their mechanics results stand, their
  household numbers are not Nb-f numbers.
- **T30 V1 decided (log (ak)):** phase B samples once per cell from the paired pool; V1 = equal to T21's manifest,
  mismatch = stop.
- T31 phase A CLOSED (E0 exact, E1 heating +205–208 %, E2 2.50 ACH50).
- **T26 ACCEPTED** (log (am)): SC0–SC5 pass; SC4 read as 0 FAIL of 31 checks. Standardized-jump trigger fired → T32.
- **T31 CLOSED, NOT RUN (log (aq)):** dr_2J-09b returned; rules 1 to 8 applied. Wall, ceiling and air-tightness
  found, but no source prints a U-value or SHGC for the dominant glazing type, so window is NOT FOUND and rule 8
  fires: WP7.3 is not run, no JSON, no partial variant. The paper states the one-envelope limitation.
- **WP10 prep DONE:** T33 (log (at)) `manuscript/prep/` response_map (42 rows), jargon_inventory, si_move_list.
  T34 (log (au)) `manuscript/draft_S2_framework.md`, 9 corrections. T35 (log (aw)) Figure 1 prompt, corrected:
  raking runs AFTER matching in the code, so WP10 orders matching (2.4) before raking (2.3). T36 (log (ax), (ay))
  `manuscript/draft_SI_model_selection.md`, accepted with 3 manager corrections and both author rulings applied.
- **T29 smoke verified, PASS 3/3 (log (br)):** two households simulated, 8,760 data rows each (8,761 lines with
  header), IDs 130228 and 79252 — T21's rebuilt draw, not the published pair. The sampling-pool hazard is
  closed for T29 by measurement, not assumption.
- **T32 ACCEPTED (log (br)):** G0 PASS (guard equals T26's λ = 0 file exactly, checksum plus 100.0 % cell match),
  SC1 PASS (within 0.012 pp), SC4 PASS (0 FAIL, reproducing T26's accepted 30/1/0 reading), SC5 PASS (max diff
  0.0012 pp). Its 1,200-run S-Revert-std campaign is submitted as `1329220`.

### 2.1b Both done, collected 2026-09-15 (logs (bb) and (bc)). Nothing to do here.
- **T37 — DONE, collected and accepted 2026-09-15, log (bb).** `manuscript/draft_S7_limitations.md` is written
  and reviewed: **ten** limitations, four trace rows re-checked at source by the manager, both rulings hold. Two
  manager corrections applied: the opening count was wrong twice (it said six, the section listed nine), and the
  tenth limitation (Saturday and Sunday pooled into one weekend pattern) was added at the T38 collection with its
  own trace row. Use it as the S7 base in step 13. Do not re-run this task.
- **T38 — DONE, collected and accepted 2026-09-15, log (bc).** `manuscript/draft_SI_schedule_completion.md`
  is written and reviewed: S.5 to S.9 plus a 17-row trace table. Four manager corrections applied, three of them
  ruling (b) repairs (the 2022 at-home rates by day type, the 2030 Saturday and Sunday rates, and the 77,313
  weekday-only count were all measured on superseded builds and are now marked PENDING). Do not re-run this task.
**Three PENDING placeholders are now live in the manuscript folder** and must be filled or cut at step 13:
the 2022 at-home rate by day-type stratum, the 2030 Saturday and Sunday rates, and the 24-cell drop-count audit
behind the sampling-pool caveat. The first two come free with any rebuilt schedule file; the third is optional
and only if the reviewer response needs more than the one audited cell.

### 2.2 Cluster snapshot, `sacct` read 2026-09-17 evening (waiter wake 4, 20:23 UTC)
**Across every 2J job ever submitted in this revision, the only non-zero exit is `1328428` (the T21 scorer,
a job-script bug, already fixed, rerun and COMPLETED as `1329216`). Nothing else has failed; nothing needs
resubmitting.** Refresh these counts with `sacct` on every waiter wake before quoting them. **Running CPUs
at this read: exactly 32** (T28 1x8, T22 2x4, T29-revert 2x4, T30 2x4) — at the promised ceiling, not over.
**Count RUNNING rows only:** summing `squeue -h -o '%C'` includes PENDING array tasks, which hold no cores,
and reported 48 against a true 28 earlier today. Never act on that sum.

| Job | What | State 2026-09-17 morning |
|---|---|---|
| 1328422 | T21 Step 8 paired runs, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328425 | T21 Step 9 activity, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328426 | T21 Step 9 baseline, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328427 | T21 A4 md5-after | **DONE**, exit 0:0 |
| 1328428 | T21 `t21_check.py` selftest + A2/A2-info | **FAILED 1:0** — argparse, superseded by 1329216 |
| 1329216 | T21 scorer, resubmitted with the `--out` fix | **COMPLETED**, exit 0:0, 00:50:25 — step 3 is live, T45 is scoring it |
| 1328429 | T32 S-Revert-std build (task 0 guard, task 1 std) | **DONE 2/2**, exit 0:0, **SCORED PASS** |
| 1328430 | T32 compare | **DONE**, exit 0:0, **SCORED PASS** |
| 1328431 | T29 staging | **DONE**, exit 0:0 |
| 1328432 | T29 smoke (2 households) | **DONE**, exit 0:0, **verified PASS 3/3** |
| 1328433 | T29 S-Partial, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328434 | T29 S-Revert, 24 tasks | 21/24 done, 2 running (`_21`,`_22`), 1 pending |
| 1328310 | T22 static-schedule arm, 24 tasks `%2` | 22/24 done, 2 running (`_15`,`_23`), 0 pending — finishes next |
| 1328419 | T30 average-profile array, 48 tasks `%2` | 40/48 done, 2 running (`_40`,`_41`), 6 pending — throttle restored to `%2` |
| 1328415 | T28 200-home sample-size array, 4 tasks `%1` | 1/4 done, 1 running, 2 pending — **slowest set left** |
| 1329220 | T32 S-Revert-std campaign, 24 tasks `%2`, 1,200 runs | PENDING on `afterany:1328434` (correct, not a problem) |

**Waiter.** A 30-minute waiter was running in the (br) session on `1328310`, `1328415`, `1328419` and
`1328434`. **It dies with that session: start a fresh one as your first act**, on whichever IDs are still
queued plus `1329216` and `1329220`. Run the poll loop directly with `run_in_background:true` — **no inner
`nohup` or `&`**, which killed an earlier attempt instantly.

### 2.3 Owed by the author (never block on these)
- **dr_2J-10 and dr_2J-11 are CLOSED, both Fable and Gemini vetted (T40 log (bm), T41 log (bn)).**
  Nothing further owed from the author on these two topics. Full record: `deepResearch/
  dr_2J-10_dr2J-11_FABLE_VETTING.md` (Fable half), `deepResearch/dr_2J-10_VETTING.md` and
  `deepResearch/dr_2J-11_VETTING.md` (Gemini half plus the merge with Fable). Headlines: dr_2J-10 Gemini
  verdict NARROWED (Chen et al. 2022 scores 5 of 6 columns, missing only C3) but PARTIALLY SURVIVES
  VETTING (its own Table B "Total Y" column undercounts 12 of 25 rows, corrected counts in the vetting
  file); dr_2J-11 Gemini verdict USABLE and SURVIVES VETTING (real post-2022 WFH decline in both Canada
  and the US, evidence against the manuscript's "persists with probability one" 2030 assumption; one
  figure, the "7.1%" 2016 baseline, NOT CONFIRMED against the real StatCan page). Both merge sections
  state the Fable structural critique and the Gemini live-search facts separately, per plan items 16-19.
  Threading items 16-19 into `manuscript/prep/response_map.md` is still owed as part of WP10 (step 13),
  not from the author.
- **dr_2J-12 CLOSED, both variants in and vetted (log (bf)).** Both reviewed the SUBMITTED text in
  `submission/archive/`, not the four redrafts. Verdict REJECT-LIKELY on both, and it survives vetting: 19
  spot-checked DOIs (Gemini) all resolved on Crossref, 12 spot-checked quotes (Fable) all genuine, no
  fabrication in either. Full vetting write-up: `deepResearch/dr_2J-12_VETTING.md`. Two headline items are not
  new (WP1 = the calibration-provenance fix, WP5 = the missing-measured-data fix, both already the critical
  path). CARRIED items now in `00_REVISION_PLAN.md` §5 items 10-15 (cheap quote-verified fixes: Motuzienė Table
  1 checkmark, a Table-5 miscite in Discussion, the missing lighting-daylight-gate sentence in §7, the EUI-vs-
  SHEU-bands contradiction between Conclusion 1 and Table 5, the circular SHEU-validation wording, the
  2030-cohort-size-is-3x-2022 arithmetic check) plus one new, currently unassigned item: the CATI-to-EQ survey
  mode change lands on the same 2022 cycle as the COVID break and the manuscript does not disclose or rule out
  the confound (needs a Limitations paragraph, WP10). The single most load-bearing finding — the only
  CI-bearing shape deltas are 2022-to-2030, not the WFH break, yet the abstract/highlights/Fig. 6 caption
  attribute them to the break — is assigned to WP1 (provisional-framing fix) + WP10 (abstract/highlights
  wording). Nothing else owed here; this line item is closed.
- **Both of these were asked on 2026-09-17, answered by the author the same day, and are now CLOSED
  (logs (bu) and (bv)). NOTHING IS OWED BY THE AUTHOR. Do not ask again.**
  - **Figure 1: DONE and ACCEPTED (log (bu)).** The author generated it; T47 verified it against the T35
    spec and it matches on every checkable item (24 labels diffed, 33 arrows read out of the generator,
    only arrow 32 dashed, 190.0 x 158.0 mm at 600 dpi, must-not list clean). Use
    `figures/Figure_01_workflow.png` (vector twin `Figure_01_workflow.pdf`). **Never cite
    `Figure_01_pipeline.png`** — that is the retired axonometric figure, restored to its own content after
    the generator overwrote it; plan §5 item 23. The generator's stray write to that filename is removed,
    so the script is now safe to rerun. Still verify the figure against the *installed* document at Step 14
    and snapshot md5s around any gate that re-runs figure scripts. One item is the author's own eye: a 100
    percent zoom or proof-print legibility check, asked for once at figure lock-in.
  - **End-use split: DONE, dr_2J-13 CLOSED, RULE 3 FIRES (log (bv), plan §5 item 24).** The return is
    vetted (`deepResearch/dr_2J-13_VETTING.md`). No measured split exists for Canada; the only one on offer
    is modelled, which the scope guard excluded in advance. The manuscript states the measured end-use
    split was unavailable and attributes the Table 5 gap to **no single end use**. The "4 to 9 times,
    unequivocally located in space heating" sentence **never appears in the paper**, and the basis behind it
    was never established anyway (heated floor space and all-fuel raw combustion energy against our
    simulated site energy). Quote nothing from the chat-side summary of that run; the saved results file is
    the record. Do not rerun the search: the positive control succeeded, so the `NOT FOUND`s are genuine
    absence, not a broken tool.

**Done 2026-09-17 (br), not owed anymore:** the T21 scorer fix and resubmission (`1329216`); the T32
scoring (G0/SC1/SC4/SC5 all PASS) and the submission of its 1,200-run campaign (`1329220`); the
retrospective verification of T29's smoke (PASS 3/3, households 130228/79252). Done 2026-09-16: Step 13's
"sole model" wording fix in `writing/submission/tables/SI/Table_B1_B2.md` (lines 9, 59); T39. Done
2026-09-17 earlier: the independent 52-reference re-verification — 2 real errors, now plan §5 items 20-21,
apply at Step 13.

### 2.4 Process warnings
Three employees broke the login-node ban in an earlier session (`mkdir` twice, `find` once). **Every brief must
name `mkdir` and `find` explicitly as forbidden.** Employees must also be told: no `2>&1`, no `2>/dev/null`
(tcsh), no python on the login node, and `-p ps -t 7-00:00:00` on every job. Add the CPU ceiling to every brief
that submits: never raise `%N` or `--cpus-per-task`, 2J stays at or under 32 CPUs.

## 3. Your queue — every remaining step, in order

Nothing local is running. Steps 1 to 6 are cluster collectors and fire as jobs finish; steps 7 onward are the
writing waves and can start at any time in parallel with the cluster.

**Step 0 — first act of the session.** Start a fresh 30-minute waiter on the still-live jobs (`1328310`,
`1328415`, `1328419`, `1328434`, `1329216`, `1329220` — drop any that have finished). Then `sacct` everything
live, refresh the ten progress bars on the checklist page (**it is at Version 41**; read the live page and
diff first — the local source file in a dead session's scratchpad went stale once, so the live page is
master), republish, and send the author one short reply. Steps 7 to 13 need no cluster and can start in
parallel at any time.

**Step 1 — T29 smoke collector: DONE (br), do not re-run.** PASS on all three checks: both households
simulated, 8,760 data rows each (8,761 lines with header), IDs **130228 and 79252** = T21's rebuilt draw,
not the published 130322/80058. Recorded in the T29 impl doc.

**Step 2 — T32 build collector: DONE (br), do not re-run.** G0 PASS (guard output equals T26's λ = 0 file
exactly: checksum plus 100.0 % cell match), SC1 PASS (within 0.012 pp), SC4 PASS (0 FAIL, reproducing T26's
accepted 30/1/0 reading), SC5 PASS (max diff 0.0012 pp). **What is left here is the campaign collector** for
`1329220`, when that array finishes: score it against the T32 doc, and confirm the households are T21's —
the wrapper was verified at submit time by reading the Montreal test cell's manifest (household 130228 at
sample 1), so the collector confirms it end to end rather than re-establishing it.

**Step 3 — T21 collector: IN FLIGHT** (`1329216` COMPLETED exit 0:0; T45, a fresh Sonnet, is scoring it now
and its report lands in `impl/2026-09-17_T45_T21_collector.md`. If that report is already in the plan log
when you read this, the step is closed; otherwise adjudicate it, do not respawn it).
Fresh Sonnet. Score A1-A6 with the restated A2 (equality against the independent engine re-draw, plus
info-only overlap with the published manifests — pre-registered wording is in the T21 doc's ledger).
A5 SHEU gates are report-only. **A6 is a stop rule: a peak shift outside 0 ± 1 h stops all paper numbers**
until the manager rules on it. Hand-check one cell's annual kWh and daily peak against the raw output before
accepting. The scorer's own selftest must be seen behaving (PASS on the clean copy, FAIL on the swapped-id
copy) in its log before any PASS it reports is trusted — that is exactly what `1328428` could not do.

**Step 4 — T28 collector** (after `1328415`'s 4 tasks; it is the slowest set left, 1/4 at (br)). Fresh
Sonnet. B1-B3 plus the hand-checks in the T28 addendum. T28 answers the 200-home sample-size question; its
numbers replace the OLD-CAMPAIGN sample-size numbers under ruling (b).

**Step 5 — T30 collector** (after `1328419`'s 48 tasks; 38/48 at (br)). Fresh Sonnet. V0-V5. **Make V1 and
V2 fail once on a fake case before trusting their PASS** (V1 = manifest equality with T21; a mismatch stops
T30). Hand-check one cell end to end.

**Step 5b — T29 revert-array collector** (after `1328434`; 20/24 at (br)). Fresh Sonnet. `1328433`
(S-Partial) is already 24/24 done, so score both scenario arms together against the T29 doc.

**Step 6 — T22 collector** (fires when `1328310` finishes; 21/24 at (br)). Fresh Sonnet. Score the
static-schedule arm, and in the same pass check the Nb-f SHEU design levels and household IDs against the
old file. That comparison decides whether any T22 cell must be re-run; say so explicitly either way.

**Step 7 — deep-research returns: CLOSED, all three pairs vetted.** dr_2J-12 (log (bf)), dr_2J-10 and
dr_2J-11 (Fable log (bm), Gemini log (bn)) are all fully vetted, nothing owed from the author. `NOT FOUND`
/ `NOT CONFIRMED` results were treated as valid, useful information throughout (dr_2J-11's system boundary,
its "7.1%" figure), never discarded or guessed at. Nothing further to do here except thread the CARRIED
items into `manuscript/prep/response_map.md` as WP10 assembles (step 13). **That threading is now DONE
(T42, log (bs)): 55 rows, dr_2J-12's items at Q10-Q16 and plan §5 items 16-21 at Q17-Q22, every one
WAITING/OPEN with its plan item cited.** `Qn` is not plan item `n` — check the row, do not assume. What is
left of this step is only to flip rows to ALREADY FIXED (citing the redraft line in `manuscript/`) as WP10
actually fixes them, and to take Q18's editorial decision when WP1 recalculates.

**Step 8 — Wave 4 re-derivations** (plan §10; can start before the cluster finishes, finishes after it).
Re-derive T06, T07 and T09/T15 on the rebuilt runs. **When T09 is re-derived, re-read the scope paragraph of
`manuscript/draft_S7_limitations.md`**: it describes the measured-data check as Toronto and Ontario electricity on
shoulder-season weekdays, sourced from the old T09 doc. No T09 number is quoted there, so ruling (b) is not
breached, but the description must still match the re-derived run (log (bb)). Under ruling (b), every number these produced on the old
campaign is replaced or dropped — check each against the T36 number trace table, which now marks the seven
OLD-CAMPAIGN / OLD-BUILD rows.

**Step 9 — WP6** (2030 and scenarios). WP6 **must deliver the clustering check that `draft_S2_framework.md`
promises in its paired-interval section**, or that sentence is cut from Section 2. Decide and record which.

**Step 10 — WP8**: confidence intervals recomputed on the corrected runs (pooled paired Student-t,
`08_simulation_val.py:951-1027`). **Step 11 — WP3**: the comparison table. **Step 12 — WP11**: figures — write
prompts only for schematic figures; matplotlib plots from frozen data are allowed and preferred. **Figure 1
is already done and verified** (log (bu)): insert `figures/Figure_01_workflow.png`, cite it under that name,
never `Figure_01_pipeline.png` (plan §5 item 23). The manager may write or replace a figure prompt on its
own judgement (author, 2026-09-17), but still never generates the image.

**Step 13 — WP10, the manuscript rewrite for Applied Energy.** Carry in: the response map (42 rows), the jargon
inventory, the SI move list, `draft_S2_framework.md`, `draft_SI_model_selection.md`, `draft_S7_limitations.md`,
`draft_SI_schedule_completion.md`, the Figure 1 prompt. **Plan §5 item 5 is already settled, do not redo it** (log (bc)): Saturday and Sunday are pooled into one
weekend pattern at the building-model interface, `07_aug_to_bem.py:34`, and the tenth limitation is already in
`draft_S7_limitations.md`. At assembly, confirm the SI appendix order and renumber S.5 to S.9 if this part does
not follow the model-selection part, and name which calendar-expansion path the campaign uses
(`create_compact_schedule` or `write_8760_schedule_csv`); no claim turns on it, but the SI should not be vague.
Order matching (2.4) before raking (2.3). Apply plan §5 items 20-21 to the new reference list (Motuzienė
et al. 2022 volume 76→77; Jalilian & Kamel 2025 restore the full subtitle). State plainly: the before/after comparison is **not household-paired
across stocks**; the one-envelope limitation; validator check 3.5; ruling (a)'s weekend limitation; and that **no measured
Canadian residential end-use split exists**, so the energy-intensity gap is attributed to no single end use
(plan §5 item 24 carries the wording, and forbids the "4 to 9 times space heating" sentence). Update
`writing/submission/tables/SI/Table_B1_B2.md` lines 9 and 59 ("sole model" wording). Re-derive or drop the seven
OLD-campaign SI numbers. The internal model label (J3) never appears in prose.

**Step 14 — WP13**: build the submission package, then run `submit_check.py` on the installed files until green.

**Step 15 — Wave 5**: write `deepResearch/dr_2J-08_presubmission_audit_prompt.md` **only after step 14 is green**.
The author runs it in Gemini and Fable 5; vet the return the same way.

After every step: append to the plan Progress Log, tick the plan §9 boxes that closed, republish the checklist
page (read live first, `node --check` the script), and **update §2–§3 of this prompt and its "Last updated" line**.
At session end, update memory `project_2j_paper_writing.md`.

## 4. First reply to the author

One plain headline on where things stand (how many cluster runs finished overnight, and whether anything failed),
3–5 plain bullets, `Evidence:`, `Next:` in 3–4 words. Nothing else.
