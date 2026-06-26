# RESUME — Opus Manager Session Handoff (Step-6 2-split, job 987039)

You are the MANAGER (Opus) in a two-agent workflow: you plan, debug, and write the prompts that spawn cheap Sonnet/Haiku employees who do all execution (monitoring, log peeks, scp, sbatch). You do NOT run monitoring/poll loops yourself. First read CLAUDE.md and memory/MEMORY.md (esp. project_step6_2split_status.md). Resume the task below as if no break happened.

## WHAT'S IN FLIGHT
3J Leg-2 "2-split" **STEP 6** = Model 2, the longitudinal occupancy forecast to 2030 (office/WFH leg). Two-channel (AT_HOME + AT_WORK), 3 WFH sensitivity bands: conservative 17.5% / hybrid 30% / fully-hybrid 40% of employed teleworking.

Prior job 982868 finished clean but **DEGENERATE**: all 3 bands identical, backcast JS = -0.0000, val_js = 0. Root cause: `Step6Dataset` self-paired each diary (encoder src index == decoder tgt index) -> the 04B translator collapsed into an identity-copier. Control probe 987027 verdict was **FLAT** — TELEWORK is NOT learnable as a conditioning signal. So the fix is **BOTH**: (A) cross-day-pairing retrain for valid drift-aware checkpoints + valid backcast, and (B) an exogenous post-hoc day-type reweight to create the 3 bands. Plus (C) anti-copy gates.

## JOB 987039 (the fix retrain)
`step6_2spl`, Speed **pg** partition, `-t 7-00:00:00`. Started ~15:37 EDT 2026-06-24.

As of handoff (~09:00 EDT 2026-06-25, ~17.5h elapsed): **RUNNING, HEALTHY**, deep in Phase 4 (W_2015_ft -> W_2022_ft), epoch ~8/30, ~1600-2000s/epoch. This is a **MULTI-DAY run (2-3 days)**, not the original ~8h guess — per-epoch cost of the heavier two-channel joint model + cross-day KNN pairing. The 7-day cap covers it; do not panic at the runtime.

Phase structure: sequential per-year fine-tunes (...->2010->2015->2022->pooled/2030), THEN backcast D1, THEN band D2 reweight.

Health so far: Phase 2 (->2010) done val_js=0.0248; Phase 3 (->2015) done val_js=0.0192; Phase 4 (->2022) mid-flight val_js~0.0278. Gate-3 epoch-1 anti-copy PASS every stage. The **NEGATIVE total loss** in fine-tune phases is **BENIGN**: the act/home/work reconstruction heads stay positive (~0.37/0.18/0.14); the negative comes from an unnamed aux/likelihood term; val_js stays small-positive (a copier would force it to 0).

**FLAG to watch:** Phase 3's COVID-check printed two WARNs — `WD AT_HOME_drift=-0.0824` ("[WARN] AT_HOME drift < +5pp") and `AT_WORK_drift=+0.1462` ("[WARN] AT_WORK drift not clearly negative"). Phase 3 = 2015 checkpoint (pre-COVID) so likely benign, BUT check the 2022/backcast COVID gate doesn't WARN the same wrong direction.

## THE 3 FIXES (already in the module)
- **A. `build_cycle_pairs()`** — cross-day KNN pairing replacing self-pairing. EXACT_COLS (AGEGRP/SEX/MARSTH/HHSIZE/LFTAG) + FUZZY_COLS (PR/CMA/HRSWRK/NOCS + TOTINC 6-quantile bins), K=5, t!=s, same CYCLE_YEAR, different DDAY_STRATA; numpy brute-force (NO sklearn — cluster env is torch/numpy/pandas only). `resample()` draws a fresh neighbour each epoch; `__getitem__` uses separate `s` (enc source) and `t` (dec target).
- **B. `_posthoc_reweight()`** — base 2030 forecast generated ONCE (shared via `_d2_cache`); each employed diary = WFH-day if business-hours (slots 11-26) AT_HOME fraction >= 0.50; AGEGRP-stratified donor draw to hit {17.5,30,40}% WFH-day share; non-employed pass through unchanged. (Replaced the dead TELEWORK-conditioning band override.)
- **C. 4 anti-copy gates** — Gate1 slot-disagreement>=5% (SystemExit if <5%), Gate2 JS>=0 & finite, Gate3 epoch-1 val_js>0 & loss check, Gate4 band shares +/-3pp & monotone — **Gate4 was SKIPPED in `--smoke`**, so 987039 is the FIRST real test of band divergence.

Predecessor archived at `...\Step6_docs\archive\3rdJ_06_longitudinalForecasting_2split.preCrossDayPairing.py`.

## YOUR JOB AT TERMINAL STATE — JUDGE, DO NOT AUTO-PASS
Do NOT rubber-stamp any in-log "PASS" line (they false-pass). When 987039 finishes, read its `.out` and verify YOURSELF:
1. Backcast (D1) JS is **REAL & small-but-positive** — NOT 0 / -0.0000. (G14 wants a GOOD fit, so small JS is correct, just nonzero.)
2. The 3 WFH bands land **~17.5/30/40% (+/-3pp)** AND WD_AT_HOME diverges across bands. (Gate 4 skipped in smoke -> first real divergence test.)
3. COVID drift gate (2022 backcast): AT_HOME drift UP, AT_WORK drift DOWN.

Only when ALL hold do YOU (manager) declare Step-6 done — never an in-log line. Then update memory `project_step6_2split_status.md` + append the Progress Log row. If it fails/degenerates -> audit the FULL chain at once, ship ONE fix bundle (no per-failure patches), resubmit at `-t 7-00:00:00`. Do NOT start Step 7 until Step-6 is truly done.

## HOW TO CHECK STATUS (cheap one-shot employee, NEVER yourself, NEVER a re-arming loop)
Spawn a Haiku one-shot (`model: haiku`) for a SINGLE peek — the user explicitly killed all continuous monitors; do not recreate them. Login-node-safe, single-file only:
```
ssh o_iseri@speed.encs.concordia.ca
sacct -j 987039 -o JobID,State,Elapsed -P
tail -n 60 /nfs/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs/step6_2split_987039.out
grep -nE "Phase|done|Backcast|BACKCAST|band|WFH|JS|Gate" on that ONE file for structure.
```

## STANDING CONSTRAINTS (still in force)
- NEVER blocking/interactive `srun` on login node — always `sbatch`, read the output file after (account-suspension risk, flagged 3x).
- NO bare `python`/`python3` on login node ever (incl. one-liners). Allowed: `sbatch`/`squeue`/`sacct`/`scancel`/`scontrol`/`cd`/`ls`/`scp`/`module load` + single-file `tail`/`head`/`grep`/`wc -l`/`cat`.
- Every submission `-t 7-00:00:00` minimum (HARD RULE #3); Speed ps/pg MaxTime = 7 days.
- Cheap models (Haiku/Sonnet) for ALL monitoring/peeks/scp/sbatch; ALWAYS set `model:` on Agent calls; min 30-min spacing; prefer one-shot checks over poll loops.
- Speed login shell is tcsh; no `2>&1` (use `>&` or omit); one short line, no backslash continuation.
- Label every command "locally" or "on the cluster". Bundle uploads (one scp/cycle). Step 4 LOCKED. Never upload the whole GSSCanada-main dir.
- Communication: casual, <=100 words unless detail requested.

## FILES
- Module (local): `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\Step6_docs\3rdJ_06_longitudinalForecasting_2split.py`
- Progress Log (local): same dir `\3rdJ_06_longitudinalForecasting_2split.md` (table `| Date | Action | Notes |` ~L739)
- Cluster dir: `/nfs/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/3J_docs_occ_nTemp/Leg2_2-split/Step6_docs`
- Cluster stdout: `step6_2split_987039.out`
- Memory: `C:\Users\o_iseri\.claude\projects\C--Users-o-iseri-Desktop-GSSCanada\memory\project_step6_2split_status.md`

## MONITORING STATE
ALL monitors killed at user request; job 987039 untouched and still RUNNING. Do NOT spin up continuous monitors. When you want status: one cheap Haiku peek, then act only on terminal results.
