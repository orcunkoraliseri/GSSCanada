# Task: Step 4 F2 retrain — stratum-bias + co-presence/activity audit

Date: 2026-04-23
Status: proposed (awaiting user approval of HP scope + 04I contract before the implementing session is triggered)

## Aim

Close the residual stratum-conditional AT_HOME bias (weekday under / weekend over by 5–14 pp) left after F1, and validate the two **unaudited output channels** in `augmented_diaries.csv`:

- **Co-presence** (9-way BCE head: alone / with-spouse / with-child / …) — drives BEM room-level occupancy multipliers.
- **Activity** (14-way CE head: Work / Sleep / Cook / Transit / …) — drives appliance & lighting schedules downstream.

Ride the chain wrapper from `step4_chain_submit.md` so the full F2 cycle (04D → 04E → {04F, 04H, 04I} → bundle) is a single submission and a single local `scp -r` pull.

## Steps

### 1. HP tuning (single-variable — not a grid)

Ranked by expected impact. F2 runs **HP-1a + HP-2 only**; HP-1b / HP-3 / HP-4 are pre-documented for F3 so attribution on F2 stays clean.

- **HP-1 LAMBDA_HOME escalation** (primary). F1's LAMBDA_HOME closed the global marginal but not the strata. Two flavors:
  - **HP-1a (run in F2):** raise scalar `LAMBDA_HOME` 2–3× the F1 value in `04D_train.py`. Cheapest possible change. Bounded at 3× to avoid trading AT_HOME for activity-distribution drift.
  - **HP-1b (deferred to F3 if HP-1a insufficient):** re-shape `marg_loss` (`04D_train.py:140` currently uses global `home_tgt.mean()` which mixes strata) as a sum over per-(target_cycle × target_stratum) observed AT_HOME references from `hetus_30min.csv`. Template is F1b from `step4_training.md` §5.
- **HP-2 min_epoch floor** (cheap guard, run in F2). Current `val_score`-based checkpoint selection can latch an under-trained epoch (seen at Option B epoch 1 vs epoch 11 in `step4_training.md` §1). Enforce `epoch ≥ min_epoch=5` before best-checkpoint updates in `04D_train.py`. One-line change in the training loop.
- **HP-3 soften post-hoc rule** (deferred to F3). The night-Sleep → AT_HOME=1 rule in `04E_inference.py::apply_posthoc_consistency` is no longer load-bearing now that H2 is rejected. When revisited, replace with observed conditional rate `p(home | night, sleep, cycle, stratum)` from `hetus_30min` (F2b template from `step4_training.md` §5).
- **HP-4 conditioning auxiliary loss** (deferred to F3 unless HP-1 alone fails). If stratum-conditional gap persists after HP-1, add a small MLP head predicting `tgt_strata` from the decoder's first-layer hidden state, aux weight λ ≈ 0.1 (F4a template from `step4_training.md` §5).

**Decision rule:** lock F2 as HP-1a + HP-2 only. If F2 does not close the stratum gap, F3 picks from HP-1b / HP-3 / HP-4 informed by the 04F + 04H + 04I output.

### 2. New 04I co-presence + activity audit diagnostic (contract only — script written in the implementing session)

- **Inputs:**
  - `outputs_step4/augmented_diaries.csv` — synthetic; carries co-presence one-hots + activity one-hots from 04E.
  - `outputs_step3/hetus_30min.csv` — observed ground truth for the same two channels.
- **Outputs:** two JSON files, each mirroring the 04H contract (per-cycle × per-stratum marginals, per-slot trajectory, scalar gap summaries):
  - `outputs_step4/diagnostics_v4_copresence.json`
  - `outputs_step4/diagnostics_v4_activity.json`
- **Co-presence check (9 classes).** For each class:
  - Per (cycle × stratum) observed vs synthetic marginal.
  - Per-slot trajectory (48 slots) of observed vs synthetic.
  - Scalars: `overall_gap_pp`, `morning_mean_gap_pp` (slots 0–13), `midday_mean_gap_pp` (slots 14–27), `evening_mean_gap_pp` (slots 28–47), `max_gap_pp`, `slot_of_max_gap`.
- **Activity check (14 classes).** Same structure. Flag any class with `|overall_gap_pp| ≥ 3` as a potential regression from the §2 JS PASS baseline.
- **Resource profile:** `ps` partition, 8 G mem, 4 cores, 30 min wall — identical to `job_04H_diagnostics.sh`.
- **Job script:** new `2J_docs_occ_nTemp/Speed_Cluster/job_04I_audit.sh`. Chain wrapper treats it as a fourth parallel branch off `afterok:$JID_E` (alongside 04F and 04H; all three only need `augmented_diaries.csv`).
- **Python entrypoint:** new `04I_audit_cpu.py`, templated on `04H_diagnostics_cpu.py`. Read-only — no model, no pipeline side effects.

### 3. Wrapper invocation + delivery contract

- **Submit (on the cluster, login node):** `./submit_step4_chain.sh F2_lambda_home_escalation`
- **squeue check (on the cluster):** `squeue -u o_iseri` — must show 6 jobs (04D running/queued; 04E/04F/04H/04I/bundle with `Dependency`).
- **Delivery folder:** `/speed-scratch/o_iseri/occModeling/deliveries/F2_lambda_home_escalation/` must contain:
  - `step4_validation_report.html` (pull locally as `step4_validation_report_v5.html` per project naming convention)
  - `diagnostics_v4.json` + `diagnostics_v4_trajectories.png` (AT_HOME, from 04H)
  - `diagnostics_v4_copresence.json` (new, from 04I)
  - `diagnostics_v4_activity.json` (new, from 04I)
  - 5 `.out` logs (04D / 04E / 04F / 04H / 04I) + `CHAIN_DONE` sentinel
- **Local pull (locally, single line):** `scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/occModeling/deliveries/F2_lambda_home_escalation .`

## Expected result

- Single command on the cluster launches the full F2 cycle.
- Global AT_HOME marginal stays within F1's ±5 pp band (no regression).
- Stratum-conditional AT_HOME gap narrows: both weekday under-bias and weekend over-bias < 5 pp absolute.
- 04I: no co-presence or activity class flagged with `|overall_gap_pp| ≥ 3`. Any flagged class becomes F3's priority, not F2's.
- 04F HTML renders on local with embedded plots (the v4 bug — 34 KB, zero `<img>` — does not recur because 04F is re-run on fresh `augmented_diaries.csv`).

## Test method

- **Before submit (cluster, single line):** `bash -n submit_step4_chain.sh job_04Z_bundle.sh job_04I_audit.sh` — all three must parse.
- **04I smoke test (cluster, CPU only — no GPU allocation burned):** run `04I_audit_cpu.py` end-to-end against the current F1 `augmented_diaries.csv` before F2 submit, so we have a **pre-F2 baseline** for co-presence / activity gaps. This is the F3 branch-decision input if F2 doesn't land.
- **Live F2 run:** `sacct -j <chain_ids> --format=JobID,Partition,State,ExitCode,Elapsed` end-state must show all COMPLETED, partitions `pg / pg / ps / ps / ps / ps`.
- **Post-run three-question protocol (same shape as F1's):**
  - (a) Did stratum-conditional AT_HOME gap close, or did only the global marginal move?
  - (b) Per-(cycle × stratum) and per-class gap for co-presence and activity: any cells `|gap_pp| ≥ 3`?
  - (c) Which §4–§7 sections in the 04F report moved vs F1 baseline (§4.2 / §4.3 / §6.2 / §7.1 / §7.4 all persisted through F1)?
- **Fail-propagation (only if not already exercised on an earlier chain):** `scancel $JID_D` mid-queue; confirm 04E/04F/04H/04I/bundle go to `DependencyNotSatisfied`.

## Risks / fallback

- **Over-escalating LAMBDA_HOME trades AT_HOME gap for activity drift.** Mitigation: HP-1a bounded 2–3× F1 value; 04I activity audit catches regressions in the same run — no blind escalation.
- **04I is new code.** Mitigation: it's a read-only diagnostic. If 04I fails, 04F still produces the HTML and 04H still produces `diagnostics_v4.json`; bundle tolerates missing files with `|| echo "WARN: missing <file>" >> CHAIN_DONE`.
- **F1 `best_model.pt` is overwritten by F2 04D.** Before submitting F2, scp `F1_*` deliveries locally and keep a cluster-side copy of `outputs_step4/checkpoints/best_model.pt` under an F1-tagged path so we can revert if F2 regresses.
- **Collision with unresolved F1 work.** Do not submit F2 until (i) F1 v4 HTML is regenerated (broken report; just `sbatch job_04F_validation.sh` on the cluster and re-pull) and eyeballed, (ii) all F1 deliverables are scp'd locally, (iii) 04I audit on F1 augmented_diaries has been run as the pre-F2 baseline.
- **Fallback:** if HP-1a / HP-2 regresses anything vs F1, revert to the saved F1 `best_model.pt` and fold findings into F3 with HP-1b or HP-4.

## Progress Log

- 2026-04-23: task spec written. F2 scope locked as HP-1a (LAMBDA_HOME × 2–3) + HP-2 (min_epoch=5 floor) + new 04I co-presence / activity audit. Implementation deferred to post-approval session; three user review gates per the plan: (a) HP scope, (b) 04I contract, (c) chain tag naming. F3 candidates (HP-1b / HP-3 / HP-4) pre-documented so the next cycle is also one step away from submit.
