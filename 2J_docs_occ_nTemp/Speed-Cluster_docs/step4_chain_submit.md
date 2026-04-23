# Task: Step 4 chain-submit wrapper

Date: 2026-04-23
Status: approved — implement before F2 submit. F1 closed the global-marginal AT_HOME gap (H2 rejected, midday gap +4.08 pp, 04H reports SKIP_GPU); F2 targets stratum-conditional bias + unaudited co-presence / activity heads and must ride the wrapper so the full cycle is one submission.

## Aim

Replace the four manual SLURM submissions for Step 4 (04D train -> 04E inference -> 04F validation -> 04H diagnostics) with a single wrapper that chains them via `--dependency=afterok`, then bundles the user-facing artifacts into one delivery folder for a single local `scp` pull.

Plumbing change only. No Python, no model, no training HPs touched. The four existing job scripts stay reusable for one-off reruns.

## Steps

1. Create `2J_docs_occ_nTemp/Speed_Cluster/submit_step4_chain.sh` (bash, run on login node only).
   - Accept optional `tag` arg; default to `$(date +%Y%m%d_%H%M)`.
   - Resolve job-script paths via explicit variables at the top of the script. Default layout assumes all five scripts sit in `/speed-scratch/$USER/occModeling/` on the cluster (flattened, matching current convention where `04H_diagnostics_cpu.py` and `04D_train.py` already run from the same working dir).
   - Pre-flight: `set -euo pipefail`, verify each job script exists, `mkdir -p logs deliveries`.
   - Submit with `sbatch --parsable` capturing each JID:
     - `JID_D` = 04D (no dep)
     - `JID_E` = 04E, `--dependency=afterok:$JID_D`
     - `JID_F` = 04F, `--dependency=afterok:$JID_E`
     - `JID_H` = 04H, `--dependency=afterok:$JID_E` (parallel with 04F, both only need `augmented_diaries.csv`)
     - `JID_I` = 04I co-presence / activity audit, `--dependency=afterok:$JID_E` (parallel with 04F and 04H; see `step4_F2_retrain.md` for the 04I contract). Submit only if `job_04I_audit.sh` exists; otherwise skip and leave `JID_I` unset.
     - `JID_Z` = bundle, `--dependency=afterok:$JID_F:$JID_H` (add `:$JID_I` when 04I is present), passing `--export=ALL,CHAIN_TAG=...,JID_D=...,JID_E=...,JID_F=...,JID_H=...,JID_I=...`.
   - Echo chain summary, delivery path, and the three monitor/post-mortem/cancel commands.

2. Create `2J_docs_occ_nTemp/Speed_Cluster/job_04Z_bundle.sh` (SLURM CPU job, partition `ps`, 2G mem, 5 min wall).
   - Reads `CHAIN_TAG`, `JID_D`, `JID_E`, `JID_F`, `JID_H` from env.
   - Creates `/speed-scratch/$USER/occModeling/deliveries/$CHAIN_TAG/`.
   - Copies into it:
     - `outputs_step4/step4_validation_report.html`
     - `outputs_step4/diagnostics_v4.json`
     - `outputs_step4/diagnostics_v4_trajectories.png` (if present)
     - `outputs_step4/diagnostics_v4_copresence.json` (from 04I, if present — see step4_F2_retrain.md)
     - `outputs_step4/diagnostics_v4_activity.json` (from 04I, if present)
     - `logs/04D_train_${JID_D}.out`, `logs/04E_infer_${JID_E}.out`, `logs/04F_valid_${JID_F}.out`, `logs/04H_${JID_H}.out`, `logs/04I_audit_${JID_I}.out` (04I log only when that job is part of the chain)
   - Writes `CHAIN_DONE` sentinel containing the four JIDs and `sacct -j ... --format=JobID,State,ExitCode,Elapsed` output.
   - Missing artifacts: `cp` with `|| echo "WARN: missing <file>" >> CHAIN_DONE` — do not fail the bundle.

3. Do not modify `job_04D_train.sh`, `job_04E_inference.sh`, `job_04F_validation.sh`, or `job_04H_diagnostics.sh`. Note that `job_04H_diagnostics.sh` currently lives at `2J_docs_occ_nTemp/job_04H_diagnostics.sh` in the repo (one level up from the other three); on the cluster all five land in the same flat working dir, so wrapper default paths are correct. If cluster layout differs, the user edits the five path variables at the top of the wrapper.

## Expected result

- One command on the cluster (`./submit_step4_chain.sh [tag]`) launches the full pipeline.
- `squeue -u $USER` shows 5 jobs: 1 running/queued + 4 with `Dependency` state.
- Any upstream failure auto-cancels downstream (state `DependencyNotSatisfied`); `scancel <all_ids>` cleans in one call.
- On success, `deliveries/<tag>/` contains HTML + JSON + PNG + 4 logs + `CHAIN_DONE`.
- Local pull (one line, **locally**): `scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/deliveries/<tag> .`

## Test method

- **Syntax (locally or on cluster):** `bash -n submit_step4_chain.sh && bash -n job_04Z_bundle.sh`.
- **First live run:** use the next real retrain cycle (do not burn a GPU allocation just to smoke-test). Verify:
  - `squeue -u o_iseri` immediately after submit shows 5 JIDs with correct `Dependency` fields.
  - `sacct -j <chain> --format=JobID,Partition,State,ExitCode` at the end shows 04D/04E on `pg`, 04F/04H/bundle on `ps`, all `COMPLETED`.
  - `deliveries/<tag>/` contains all six expected files.
- **Fail-propagation (do once, cheap):** submit the chain, then `scancel $JID_D` mid-queue; confirm 04E/04F/04H/bundle go to `DependencyNotSatisfied` and clear with `scancel`.

## Risks / fallback

- **04H path drift:** on the cluster all scripts are flattened into one dir so wrapper defaults work; if repo layout changes the user must update the five path vars at the top. Keep them visible and labelled.
- **Silent non-convergence:** `afterok` checks exit status, not model quality. A model that overfits or collapses still exits 0 and triggers 04E. Out of scope for this task; revisit with a `check_loss.py` gate between 04D and 04E only if it becomes a real problem.
- **`pg` queue wait between 04D and 04E:** scheduler-dependent; acceptable vs manual.
- **Collision with the in-flight F1 cycle (jobs 901399 / 901476 family):** do NOT invoke the wrapper until that cycle finishes and we've decided on F2/F3. Stated in the wrapper header as a usage warning.
- **Fallback:** the four original job scripts still work standalone. Zero regression surface.

## Progress Log

- 2026-04-23: task spec written. Implementation deferred — waiting on F1 retrain (job 901399) + 04E (job 901476) results and the post-04H branch decision (retrain_min_epoch_5 / soften_posthoc_rule / HP_LAMBDA_HOME_escalation) before we commit to another full retrain cycle that would actually exercise the wrapper.
- 2026-04-23 (later): F1 verdict in — H2 rejected, T3 midday gap −27.8 → +4.08 pp, 04H reports SKIP_GPU, trajectories v4 clearly closer to observed than v2/v3. Global-marginal AT_HOME gap closed; residual weekday/weekend stratum-conditional bias (5–14 pp split) + unaudited co-presence (9-way BCE) and activity (14-way CE) heads remain. Status flipped to **approved — implement before F2 submit**. Added: (i) 04I audit job as a fourth parallel branch off `afterok:$JID_E`; (ii) bundle copies new `diagnostics_v4_copresence.json` / `diagnostics_v4_activity.json`. F2 HP scope (HP-1a LAMBDA_HOME escalation + HP-2 min_epoch floor) specified in the new `step4_F2_retrain.md`.
