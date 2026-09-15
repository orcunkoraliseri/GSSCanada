# 2J manager prompt — RESUME the Applied Energy resubmission (paste whole into a new session)

First written 2026-09-15 by the outgoing manager session. **Kept current: the manager rewrites §2 and §3
after every task completion** (author request, 2026-09-15). Last updated: 2026-09-15, plan log entry (ay).
Model: Opus (manager). Employees and collectors: Sonnet, named explicitly on every Agent call.

---

## 0. Who you are and the standing instructions

You are the **manager** of the 2J rejection revision. The paper was rejected by Building Simulation on
2026-09-15. Target venue is **Applied Energy** (author decision; fallback Sustainable Cities and Society).

Author instructions that still bind, verbatim where quoted:
- "continue until the end, do not stop the progress anymore for questions". You take design decisions
  yourself and record them in the plan's Progress Log and the task doc. Ask the author only for inputs
  only they hold (the SHEU end-use split; running deep-research prompts).
- Use cheaper agents (Sonnet), model named explicitly. **One fresh agent per task, never resume a
  finished one.** Employees submit, write the JobID to the task doc, end the turn. They never wait.
- Use the Speed cluster at full speed (account cap 32 CPUs total), `sbatch` only.
- Option (a) is decided: 2022 is rebuilt from 2022-cycle diaries only; 2030 is built by D1 on the rebuilt
  stock. Do not re-open it.
- **Update this prompt (§2 and §3, plus the "Last updated" line) after every task completion**, in the same
  turn as the Progress Log entry and the checklist republish.
- "udpate artifact everytime" (2026-09-15): republish the checklist page after EVERY step, not only task closures.

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

Engine facts (verified, do not re-derive): cell label `f"{archetype}__{city}"`; archetypes SingleD,
OtherDwelling, MidRise, HighRise; cities Toronto_5A, Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B,
Winnipeg_7A; array task id = arch_idx*6 + city_idx. `run_paired_mc.py` has no `--code-root`: run the copy in the
shared tree `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (T22's tree never had the driver; log (ag)). `--sched-dir` expects plain `BEM_Schedules_{y}.csv`. **The sampling pool = households passing `validate_household_schedule` on the loaded file(s), so it depends on schedule CONTENT**: any run meant to reuse T21's households must use T21's paired pool or T21's manifest, never a fresh draw on another file (log (ak), (am)). Stock weights are archetype-only, split
equally over cities. CI = pooled paired Student-t (`08_simulation_val.py:951-1027`). Metrics in
`08_simulation_plots.py` (annual kWh :340,361; daily peak :377; circular peak hour :278-285; load factor :385;
midday share [9,17) :387; circular SD :290; morning-leaning share :914-915).

## 1. Read these first, in order

1. `2J_docs_occ_nTemp/writing/submission/rejection revision/00_REVISION_PLAN.md` — §2 reviewer triage,
   §3 work packages, §9 closure boxes, §10 waves, and **the Progress Log from entry (aa) to the end**.
   The log is the state.
2. The task docs of everything in flight (§2 below), Ledger and Manager addenda first.
3. `deepResearch/00_README_deepResearch.md` (vetting list, venue decision rule).
4. Memory: `project_2j_paper_writing.md` (update it at the end of your session).

All `impl/` and `deepResearch/` paths are under `2J_docs_occ_nTemp/writing/submission/rejection revision/`.

Progress checklist page for the author: https://claude.ai/artifact/4emZkRdASTDUtvXSRtWPVe (source HTML
`C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\3104eb58-cbdd-4775-8be0-71261110f8f2\scratchpad\2j_resubmission_tracker.html`;
if it is gone, `Artifact action:read` the URL and rebuild the file from it). **Always read the live page and
diff before republishing; extract the script and `node --check` it; never pass `favicon` again.** The top panel "Right now" holds one
progress bar per cluster job (cells done of total, from `sacct`); refresh its counts on every waiter wake
(author asked for it, Version 15, because monitoring was hard).

## 2. State (2026-09-15, entry (ay))

Done and trusted:
- T01–T19, T23–T25, T27 (see log). T17: Speed reproduces the local campaign. T18: control arm reproduces the
  published 2022 files exactly. T23: the schedule fallback path gives identical values; no correction.
- **T18c / choice rule (entry (aa))**: the frozen 2022 stock is **Nb-f**, all 144,465 households, 6,934,320 rows.
  Validator check 3.5 fails on Nb-f (75.04 % vs 72.3 %, band not moved): a limitation.
- **T20 CLOSED** (log (ah)): N0–N3 all PASS; household-ID sets of 2030 main and null equal Nb-f 2022 (job 1328408).
- **Shared Step-8 code tree** `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (log (ag)).
- **T21 sample question CLOSED (log (ak), T21 doc last ledger).** Staged files byte-equal to T18c/T20 outputs. The
  rebuilt schedules change which households the engine's sanity check drops, so the paired pool (16,326 for
  SingleD Montreal) differs from the published one (16,208) by 320 households and seed 42 draws a different sample
  (130228/79252 vs published 130322/80058, which the engine reproduces on the published files). **Basis change:
  A2 = equality with an independent engine re-draw on the staged files (seen failing first) + info-only overlap
  with the published manifests.** The paper must say the before/after comparison is not household-paired across
  stocks. T21 smoke PASS. T30's and T31's smokes ran on the PUBLISHED schedules: their mechanics results stand, their
  household numbers are not Nb-f numbers.
- **T30 V1 decided (log (ak)):** phase B samples once per cell from the paired pool; V1 = equal to T21's manifest,
  mismatch = stop.
- T31 phase A CLOSED (E0 exact, E1 heating +205–208 %, E2 2.50 ACH50). T29 READY (nothing submitted).

In flight (JobIDs in each task doc's newest ledger):
- **T21 phase B:** Step 8 array 1328422, Step 9 activity 1328425, Step 9 baseline 1328426 (24 tasks each, `%4`);
  A4 md5-after 1328427 and `t21_check.py` 1328428 (selftest, then restated A2 + A2-info), both `afterany`.
- **T30 phase B:** re-smoke 1328418 PASS (manager read, doc); array 1328419 (48 tasks, `%2`) running.
- **T28 phase B:** array 1328415 (4 tasks, `%1`) running; no collector job yet.
- **T26 ACCEPTED** (log (am)): SC0–SC5 pass; SC4 read as 0 FAIL of 31 checks. Standardized-jump trigger fired → T32.
- **T29 phase B SUBMITTED** (log (ao)): fixed-manifest wrapper (simulates T21's Step-8 manifest rows on the S-Partial / S-Revert files). Staging 1328431, smoke 1328432, arrays 1328433 (S-Partial) and 1328434 (S-Revert), 24 tasks each, `afterok` on smoke + staging + T21 Step 8 1328422, `--nice=100`.
- **T32** S-Revert-std build SUBMITTED (log (an)): array 1328429 (task 0 guard, task 1 std), compare 1328430 `afterok`
  (spec §5; guard task must equal T26 λ = 0 exactly).
- **T22:** static-schedule arm 1328310, 14 of 24 cells done or running.
- A background waiter polls every 30 min and fires when any of T29 smoke 1328432, T32 compare 1328430, T22 1328310 or T21 check 1328428 leaves the queue; it prints which. Restart it (minus the finished IDs) after each wake.

**T31 CLOSED, NOT RUN (log (aq)):** dr_2J-09b returned; rules 1 to 8 applied in the T31 doc. Wall, ceiling and
air-tightness found, but no source prints a U-value or SHGC for the dominant glazing type, so window is NOT FOUND
and rule 8 fires: WP7.3 is not run, no JSON, no partial variant. The paper states the one-envelope limitation.
Owed by the author: run `deepResearch/dr_2J-10_novelty_matrix_search_prompt.md` and
`dr_2J-11_wfh_trajectory_and_tradeoff_prompt.md` (log (ar)); vet each return with the README 7 steps before any citation.
Later, once: the SHEU end-use split (never block on it).
Process: three employees broke the login-node ban this session (`mkdir` twice, `find` once). Every brief names
`mkdir` and `find` explicitly.

## 3. Your queue, in order

1. Phase-B submissions are done (log (al)); nothing to do for them until the waiter fires. WP10 prep T33 (response
   map, jargon inventory, SI move list) and T34 (Section 2 framework draft with traced equations) launched (log (as)):
   T33 DONE and accepted (log (at)): `manuscript/prep/` response_map (42 rows), jargon_inventory, si_move_list.
   T34 DONE (log (au)): `manuscript/draft_S2_framework.md`, every trace row re-read, 9 corrections. WP6 owes the
   clustering check the draft promises in its paired-interval section (or cut that sentence).
   T35 (Figure 1 workflow image prompt) and T36 (SI draft: model selection and held-out-year validation, every
   number re-read from source) launched (log (av)). T35 DONE (log (aw)), prompt corrected: raking runs AFTER
   matching in the code, so WP10 orders matching (2.4) before raking (2.3). Author owes Figure 1 image (not urgent).
   T36 DONE (log (ax)): SI draft accepted with 3 corrections. The backcast weekend ceiling was raised after the
   result; the SI says so and the main text must never say the weekend passed. Seven OLD-campaign numbers in its
   trace table must be re-derived on the rebuilt runs or dropped. No helper is running now; only the cluster.
   AUTHOR RULINGS (log (ay)), binding on every later task: (a) the diary-distance ceiling is 0.10 for every day
   type, the weekend misses it, the manuscript says so, the widening to 0.20 is disclosed once and used nowhere,
   and the synthesized weekend days are a stated limitation; (b) old-campaign numbers are re-derived on the
   rebuilt runs or dropped, and old and rebuilt numbers never share a table.
2. T26 DONE (log (am)); T29 and T32 JobIDs confirmed (log (an), (ao)). When smoke 1328432 finishes, a fresh collector reads the T29 smoke (both
   households simulated, 8,760 rows, IDs 130228/79252; else scancel the array). When T32 finishes, a fresh collector
   scores G0 guard, SC1, SC4, SC5 and the reported numbers; on PASS, brief 1,200 S-Revert-std runs with T29's wrapper.
3. T30 re-smoke: DONE, PASS (manager read).
4. When T21's arrays finish: fresh T21 collector (A1–A6 with restated A2 and A2-info; A5 SHEU gates report-only; A6
   peak shift outside 0 ± 1 h stops paper numbers). Then T28 collector (after T21 Step 8 and its own array; B1–B3 +
   addendum hand-checks) and T30 collector (V0–V5; make V1/V2 fail once on a fake case first; hand-check one cell).
5. T31: CLOSED without runs (log (aq)). Do not reopen; WP7 step 3 is dropped, WP10 states the one-envelope
   limitation.
6. Collect T22 when 1328310 finishes; the collector also checks the Nb-f SHEU design levels and household IDs
   against the old file, which decides whether any T22 cell reruns.
7. Wave 4 (plan §10): re-derive T06, T07, T09/T15 on the new runs; WP6 on 2030 and scenarios; WP8 CIs on corrected
   runs; WP3 comparison table; WP11 figures; WP10 rewrite for Applied Energy (state the re-drawn sample); WP13
   package. Ask the author once for the SHEU end-use split. Optional: seed-42 rerun of one historic year (T24).
8. Wave 5: write `deepResearch/dr_2J-08_presubmission_audit_prompt.md` **only after WP13 is built and
   `submit_check.py` is green on the installed files.** The author runs it in Gemini and Fable 5.

After every task completion: append to the plan Progress Log, tick the plan §9 boxes that closed,
republish the checklist page (read live first), and **update §2–§3 of this prompt**.

## 4. First reply to the author

One plain headline on where things stand (has the 2030 build finished and passed its checks), bullets,
`Evidence:`, `Next:`. Nothing else.
