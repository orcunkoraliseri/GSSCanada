# MANAGER KICKOFF PROMPT — 3J Leg-3 (4-split) — CONTINUE AT STEP 5
### Paste this whole file into a fresh manager session (Opus). Authored 2026-07-20 by the Step-4-closeout manager session. Supersedes `2026-07-18_leg3_execution_kickoff.md` for the *entry point* only (that file's rules still apply verbatim).

---

You are the **manager (Agent1, Opus)** for the 3rd-Journal **Leg-3 four-channel pipeline** (Residential + Office + **Retail** + **Hotel**). You plan, debug, review, and author employee prompts; you do **not** execute multi-step implementation yourself. Employees (Sonnet, Haiku for mechanical/monitoring/scp work) execute one task at a time from the step runbooks and append a Progress Log entry. Every employee prompt must state: *"You are the employee. Execute the task below and append a Progress Log entry on completion."*

**The runbooks under `Leg3_4-split/Step{1..9}_docs/` are the single source of truth — execute as written, do not redesign.** If a decision-level question surfaces, stop and ask the user; never decide silently.

## What is already DONE (do not redo)

- **Steps 1–4 COMPLETE.** Design frozen 2026-07-02; all 17 runbooks written 2026-07-18; Steps 1–3 done 2026-07-19 (Step 3 built `retail_30min.csv` (64,061×49), all 6 legacy outputs bit-identical to Leg-2, validator 120P/13W/0F).
- **STEP 4 CLOSED 2026-07-20 — paper-ready, 0 genuine model defects.** Seed 3 selected from a 5-seed joint sweep. Post-hoc chain ran clean: **04L** (joint rake, GPU, job 1128036) → **04M** (min-dwell, job 1128047) → **04T** (act-rake, job 1128070), all COMPLETED 0:0, 04T byte-identity guard held (hom30/wrk30/ret30 identical to input; only act30 changed).
  - **LOCKED PRODUCTION POOL (this is the Step-5 input):**
    `Leg3_4-split/Step4_docs/outputs_step4/sweep/seed_3_raked3_mindwell_actv/augmented_diaries.csv`
    — **on the CLUSTER**, 192,183 rows, ~399 MB, with `ret30_001..048` present. Columns: act30 + hom30 + wrk30 + ret30 (48 each) + 9 co-presence + demographics + CYCLE_YEAR + DDAY_STRATA + occID + IS_SYNTHETIC.
  - **⚠️ The pool CSV is NOT local yet** — only the validation report (HTML+TXT) was scp'd down. **Step 5 runs LOCALLY, so the first prerequisite is to scp the locked-pool `augmented_diaries.csv` from cluster → local** (delegate to a cheap employee).
  - **Final validator scorecard (job 1128130): 149 PASS / 16 WARN / 1 FAIL.** The sole FAIL is **OW5** (office day-type ordering) — a documented **non-blocking, unobservable-by-design** gate (GSS = one diary-day/person → per-respondent weekday≥Sat≥Sun has no ground truth), **identical to Leg-2's sole FAIL** (Leg-2 61.4 % / Leg-3 58.2 %; REG-4 parity `['OW5']==['OW5']`). Full explanation + paper-ready caveat = the **⚠️ note at the top of `Step4_docs/3rdJ_04_augmentationGSS_4split_val.md`** and its 2026-07-20 Progress-Log entries. **Treat OW5 as inherited/documented; do not try to "fix" it.**
  - Two spec-conformance fixes were made during closeout (neither moved a threshold, both documented): RW6 severity → WARN (matches spec), RW7 QC<AB sub-check → WARN (evidence: diag job 1128112 proved the ordering isn't robust in the observed data). REG-1 was re-run against the correct **post-act-rake** Leg-2 baseline `R5_raked_mindwell_actv2` (0.0166→0.00003 PASS) — that baseline now lives on the cluster.

## STEP 5 — what to execute now

**Runbook:** `Step5_docs/3rdJ_05_censusLinkage_4split.md` + `Step5_docs/3rdJ_05_censusLinkage_4split_val.md`. **Runs LOCALLY (no sbatch).**

**Aim:** extend the Leg-2 Census–GSS linkage to carry the *third* GSS channel — every matched diary now brings `act30 + hom30 + wrk30 + ret30 + 9 co-presence` onto its Census person. **The matching machinery is unchanged** (4-tier demographic fallback, day-type 5:1:1 seed 42, authority rules, aggregation stages all ported verbatim); `ret30` rides through `expand_slot_schedules` exactly as `wrk30` does — **channels are carried, never re-derived.**

**The scripts do NOT exist yet** — only the two runbook `.md` are present in `Step5_docs/`. Task 1 is to **build** `3rdJ_05_censusLinkage_4split.py` + `3rdJ_05_censusLinkage_4split_val.py` by forking the Leg-2 originals and applying the five deltas, then run the local stage chain.

**Fork base:** `../../Leg2_2-split/Step5_docs/3rdJ_05_censusLinkage_2split.py` + `..._2split_val.py` (use the current/improved Leg-2 versions — Leg-2 Step-5 had a 2026-07-10 improvement pass; confirm you're forking the live non-archived file, not a `archive/*_pre*` predecessor).

**Leg-3 deltas (everything else verbatim):**
- **Delta A — channel carry-through:** add `ret30_001..048` to the carried column set in `expand_slot_schedules` and every downstream schema list (Full_Schedules ~248 → ~296 cols).
- **Delta B — aggregation (5E):** `ret30` is a **per-person population-fraction channel — NEVER HH-maxed** (same rule as `wrk30`; only `hom30` is HH-maxed). Step-7's retail product consumes the population-level weighted mean.
- **Delta C — exclusion (5H):** unchanged (AT_HOME < 0.30 drop) — retail plays no role.
- **Delta D — join-key connectivity audit (the PR-remap lesson):** before the full run, verify the domain overlap of **every** match key (AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA, DDAY) between census and the new pool. One diagnostic function, run in `--smoke`. (In Leg-2 a silent PR coding mismatch confined matching to ~30 % of the pool while tier rates looked healthy.)
- **Delta E — validator:** new **Section 3r** (AT_RETAIL consistency R1–R4) + **Section 0** (join-key connectivity 0.1/0.2), per the val doc.

**CLI (local, in order):** `--smoke` → validator `--smoke` → `--full` → `--aggregate` → `--bem` → `--exclusion` → validator. Target **0 new FAIL** beyond the inherited/documented ones; expect a scorecard comparable to Leg-2's 22P/1W/1F class plus Section 0 + 3r PASS.

## ⚠️ Step-5 non-negotiable disciplines (Leg-2 lessons, memory-flagged — enforce in every employee prompt)

1. **Frame discipline — re-derive, never assume.** Do NOT carry the Leg-2 frame constants (23,150 HH / 29,538 stock / 735 excluded). **Re-derive every frame count from THIS run's own `Full_Aggregated` output** and record them in the Progress Log. Verify the aggregate was regenerated from the *same run's* `Full_Schedules` (the Leg-2 internal-staleness bug: a June aggregate disagreed with its own schedules on 43.7 % of rows).
2. **Compare SETS, not counts.** When comparing frames across runs, compare household-ID **sets** (`set` equality), never counts — a matching count is not a matching set (the Leg-2 re-matching scare came from exactly this).
3. **Byte-identity guard.** After every stage that touches only one channel, assert the *other* channels' columns are byte-identical (`np.array_equal`) — the Leg-2/Leg-3 04T guard pattern.
4. **Pool provenance:** the diary pool is the **Leg-3 locked pool** (with `ret30_*`), NEVER the Leg-2 pool. md5 it once local, record it.
5. **Inherited Step-4 FAIL (OW5) is documented/non-blocking** — Section 3 (W1–W4 AT_WORK) inherited FAILs persist at similar magnitude; a *materially worse* value than the Leg-2 record is a new WARN, not a silent pass.

## Global rules (full text in CLAUDE.md + the runbooks) — still in force

- **Cluster (when Steps 6/8 arrive):** `sbatch` ONLY, never blocking `srun`, no bare python on `speed-submit2`, single-line commands, **`-t 7-00:00:00` on EVERY job**, ≥30-min monitoring spacing, **no polling loops** (the user's standing directive — submit, capture job id, read later; one-shot status reads OK). Login shell is tcsh → wrap remote multi-command work in `ssh speed bash -s <<'REMOTE' … REMOTE`.
- **Cost:** poll/peek/scp/log-tail/big-file-scan = Haiku/Sonnet employees, **never Opus**. Never scan the 399 MB pool in your own context — write the extraction script, hand it to a cheap employee.
- **Archive the predecessor** before editing any file (`archive/<name>.<date>_pre<Fix>.<ext>`); new outputs to NEW dirs, never overwrite pipeline output dirs.
- **Verify claims from the artifact, not the log** — re-derive every load-bearing number from the file's own columns.
- **Never relax a gate threshold to clear a FAIL** — relabel + document with evidence (the RW6/RW7 closeout is the template: evidence first, then reclassify, never silent).
- **User checkpoints:** decision-level trade-offs → stop and ask. Append-only Progress Logs; non-closure discipline ("Step 5 NOT done") until the validator signs off at 0 new FAIL (or documented WARN/INFO). **Update the auto-memory Leg-3 status entry (`project_3j_leg3_4split_status.md`) at step closure.**

## First actions for this session

1. Read the two Step-5 runbooks end-to-end + the Leg-2 Step-5 fork bases (main `.py` + val `.py`) + the Leg-2 Step-5 val doc (for the inherited gate thresholds + the 2026-07-10 improvement context).
2. Confirm the local inputs exist: `0_Occupancy/Outputs_Aligned/Aligned_Census_2025.csv` (~30,273 rows — re-verify) and `0_Occupancy/processed/office_archetype_lookup.csv`. **Delegate the scp of the locked-pool `augmented_diaries.csv` (cluster → local Step4_docs pool dir) to a cheap employee** — Step 5 needs it locally.
3. Author the Step-5 build employee prompt (fork + Deltas A–E), then the run/validate prompt. Keep the frame/set/byte-identity disciplines explicit in each.
4. After the validator passes (0 new FAIL), append the Step-5 Progress Log with the **re-derived frame counts of record**, update the auto-memory, and report to the user before moving to Step 6.

Bonne exécution.
