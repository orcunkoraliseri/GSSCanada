# RESUME — Sonnet Manager Session (3J Leg-2 "2-split")

**Paste this whole file as the first message of a fresh Sonnet session to continue.**
Last updated: **2026-07-02 — 🟢 OFFICE WFH BUG FIXED · AUTONOMOUS CHAIN IN FLIGHT · SONNET CAN DRIVE
THE TAIL.** The Opus-worthy work is DONE (bug root-caused + fixed, scorecard gates designed, the whole
job chain wired). What remains is a mechanical runbook — a Sonnet manager can drive it end-to-end and
only needs to escalate to the user (who can bring Opus back) if something genuinely breaks in a
non-obvious way. **First read CLAUDE.md and memory/MEMORY.md** (esp. `project_step8_office_wfh_bug.md`,
`project_step9_2split_status.md`), then continue from §6.

**The bug (for context):** the office channel was simulated with NO working WFH modulation — all 7
scenarios byte-identical (peak/occ/shape/energy). Root cause: `office_integration.py` read the
pre-v24.2 zone field `Zone_or_ZoneList_Name`, but E+ v24.2 renamed it → every zone read as "" → all
tagged 'skip' (`n_office_zones=0`) → OFC_* schedules appended but never wired → E+ ran the prototype
`NECB-A-Occupancy` for all scenarios. FIXED (`_get_zone_name` v24.2-robust helper + corrected PEOPLE
`Number_of_People_Schedule_Name`); smoke-validated (job 1057831: n_office_zones 0→6, HOURLY_DIFFER).
Re-sim confirmed working: building `Office_Knowledge__Tall__5A` now has 7 distinct md5s and a monotone
occupancy spread (2030 cons 5884 > hyb 5269 > full 4804 occ-h). Residential was never affected.

---

## 0. Who you are

You are the **MANAGER (Sonnet)** driving the remaining tail of the GSSCanada occupancy
modeling research (3rd journal = **"3J"**, Leg-2 = **"2-split"** = two-channel
AT_HOME + AT_WORK joint occupancy model). The user explicitly handed this tail to Sonnet because
the hard design/debug work is finished and what's left is a concrete runbook (§6).

- **You MAY execute the §6 runbook directly** — it's mechanical (watch a job chain, pull outputs,
  parse a scorecard, report numbers). This is a sanctioned runbook + the user confirmed Sonnet
  drives it, so you are "manager-as-employer" for this cycle, not plan-only.
- **Still offload the truly repetitive/heavy bits to a `model: sonnet` (or haiku) employee** —
  large-file scans, multi-file scp, long log parsing. Prefer a silent background `Monitor` bash
  poll loop over an agent for *waiting* on a job (zero model tokens while polling); min ~30-min
  spacing; never a live poll loop in your own turns.
- **Escalate to the user (who can re-summon Opus) ONLY for genuine debugging** — a chain job
  FAILs for a non-obvious reason, a gate flips FAIL unexpectedly, or the office signal still looks
  wrong after the fix. Don't burn cycles guessing at a hard bug; flag it with the log tail.
- Communication: casual, ≤100 words unless detail requested. Label commands "locally"/"on the
  cluster." End with the literal next command when you hand one off.

## 1. HARD RULES (never violate — account-suspension risk)

1. **NEVER** run a blocking/interactive `srun` (or any python/computation) on the Speed
   **login node** `speed-submit2`. ALWAYS `sbatch` (fire-and-forget), then read the output
   file. Flagged 3× — one more = suspension = all progress lost.
2. **NO bare `python`/`python3` on the login node — ever** (incl. one-liners). Allowed on
   login node: `sbatch, squeue, sacct, scancel, scontrol, cd, ls, scp, ssh, module load`,
   single-file `tail/head/grep/wc -l/cat`. Anything importing pandas/numpy/torch/eppy or
   iterating dirs → `sbatch`.
3. **EVERY job submission MUST request `-t 7-00:00:00`** (1-week min). Speed ps/pg MaxTime =
   7 days. A 1h cap once killed control job 987005 with empty output.
4. Speed login shell is **tcsh**: no `2>&1` (use `>` only; SLURM captures stderr to
   `--output`); one short line per command, no `\` continuation.
5. **Label every command "locally" or "on the cluster."**
6. **Bundle uploads** — one upload cycle; never file-by-file across cycles. Never upload the
   whole `GSSCanada-main/` dir; only named files/dirs.
7. Before any `sbatch` handoff, scan script imports — ensure eppy/pandas/numpy/torch/etc.
   exist in the cluster env (`envs/step4`); add a precheck line if unsure.
8. Archive predecessor (`cp` to `archive/`) before any edit. Update progress logs
   **live/incrementally**, not batched.
9. **Full audit, no patches**: when one cluster cycle reveals a bug, audit the whole chain and
   ship ONE fix bundle.

## 2. Cluster facts (Speed @ Concordia)

- host: `o_iseri@speed.encs.concordia.ca` (passwordless ssh/scp from this Windows box via Git
  Bash); login node = submission only; GPU partition = `pg`, CPU = `ps`.
- python: `/speed-scratch/o_iseri/envs/step4/bin/python`
- EnergyPlus 24.2 SIF: `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`
- Step-8 scratch dir: `/speed-scratch/o_iseri/step8_2split/` — upload tree under `upload/`,
  logs `logs/`, residential output `campaign/`, office output `office/`, agg tables
  `upload/…/Step8_docs/outputs_step8/agg/`.
- Step-4 base ckpt (LOCKED): `…/Step4_docs/outputs_step4/sweep/R5_lr1e4/checkpoints/best_model.pt`

---

## 3. WHERE WE ARE — Steps 1–7 DONE; Step 8 VALIDATED end-to-end (both channels); §8D DONE

**Steps 5/6/7 closed** (memory `project_step{5,6,7}_2split_status`). Step-7 deliverables in
`Leg2_2-split/Step7_docs/outputs_step7/`: residential `BEM_Schedules_2split_{2022,2030_*}.csv`
(REPLACE) + office `office_presence_multiplier_{2022,2030}.csv` (MODULATE).

**Step 8 = two-channel EnergyPlus simulation — COMPLETE & VALIDATED.** All in
`Leg2_2-split/Step8_docs/`. Scope (locked): 7 scenarios both channels
(`2005 2010 2015 2022 2030-conservative 2030-hybrid 2030-fullyhybrid`); full coupling
People+Lights+Equipment; HVAC/DHW code baseline; peak densities never modified.
- **Residential campaign (job 1029756): DRAINED CLEAN** — 8,400 cells (4 arch × 6 CZ × 7 scen
  × N=50 paired MC), 168/168 tasks ok, 0 errors. Symlink/bind bug resolved (`--bind
  /nfs/speed-scratch`).
- **Office campaign (job 1048238): DRAINED CLEAN** — 252 deterministic runs (3 arch ×
  Tall/SuperTall × 6 CZ × 7 scen).
- **§8E validation scorecard (job 1053668):** 27 PASS / 0 WARN / 13 INFO / 0 FAIL. Plotted
  re-run (job 1053902) confirmed the "no-plots" bug fixed (5 embedded charts).
- **§8D aggregation + validation refresh (job 1053986): COMPLETE 2026-07-01** (COMPLETED, exit
  0, Elapsed 01:52:25). Two-pass "summarize-on-read": `3rdJ_08_simulation_2split_agg.py`
  streamed all 8,652 runs (8,400 resid + 252 office) → `outputs_step8/agg/{agg_diurnal(1.28M
  rows),agg_annual,agg_meta,agg_peak(8,652 each)}.csv`; then `3rdJ_08_simulation_2split_val.py`
  re-ran with §4/§5/§7 (+§6.1/6.4–6.7) now reading real agg tables. **Scorecard 45 PASS / 1 WARN
  / 13 INFO / 0 FAIL; 8 embedded charts.** HTML pulled local:
  `Leg2_2-split/Step8_docs/outputs_step8/step8_validation_report.html` (717,173 bytes).
  - **The one WARN (non-blocking, expected):** SingleD median EUI 213 kWh/m² outside SHEU band
    [131–186] — pre-documented basis mismatch (our EUI = site energy ÷ *conditioned* area incl.
    basement; SHEU = heated area *excl.* basement, so conditioned-basis SingleD reads high).
    Other 3 archetypes in-band.
- **Step-9 office EUI benchmark gate (job 1054800): DONE & PASSING 2026-07-01** (COMPLETED, exit
  0, Elapsed 00:08:35 — fast Pass-2 re-validate, agg tables reused). Both office deepResearch
  prompts landed and are encoded in `3rdJ_08_simulation_2split_val.py`: `OFFICE_EUI_BAND =
  (135,100,200)` kWh/m² (as-modelled NECB2020/90.1-2019 DOE-PNNL Tall/SuperTall prototype — our
  IDFs ARE these; the pass criterion) + `OFFICE_EUI_EMPIRICAL = (230,170,360)` (SCIEU/CEUD measured
  stock, INFO context only). Result: **§4.3-office median office EUI 180 kWh/m² PASS** (in-band,
  per-arch range 160–216); §4.4 empirical INFO. **Scorecard flipped 45→46 PASS / 1 WARN / 13 INFO
  / 0 FAIL** (the office §4.3 INFO→PASS). Refreshed HTML 724,540 bytes, 8 charts (office EUI panel
  now bars+band), pulled local byte-identical. This closes the office half of 3J Step 9 (the
  mechanical half — Lights/Equipment × AT_WORK presence — was already in Step 8 via OD-8B).

Key files: `3rdJ_08_simulation_2split.md` (design + live Progress Log — canonical),
`…_val.md` (validation spec), `3rdJ_08_simulation_2split_agg.py` (NEW §8D aggregator),
`3rdJ_08_simulation_2split_val.py` (validator, §8D-extended), `run_aggregation.sh`,
`eSim_bem_utils_3J/` (engine, `plotting.calculate_eui`).

## 4. WHAT'S DONE — full pipeline through Step 8

Steps 1–7 closed; Step 8 built, corrective-cycled, both campaigns drained clean, validated
end-to-end (§8E scorecard + §8D EUI/load-shape rollup). Two-channel campaign is now a complete,
validated dataset ready to write up. The 13 INFO gates are mostly office-side reported metrics
(no numeric benchmark band encoded yet) + a few informational cross-channel notes — none are
blockers.

## 5. WHAT'S NEXT — paper reporting

The dataset + all gates are closed. One thread remains:

1. ~~**Office EUI numeric gate.**~~ **DONE 2026-07-01** (job 1054800). Both deepResearch prompts
   landed; office band encoded (`OFFICE_EUI_BAND=(135,100,200)` as-modelled PNNL = pass criterion;
   `OFFICE_EUI_EMPIRICAL=(230,170,360)` SCIEU = INFO). §4.3-office median EUI 180 kWh/m² PASSES.
   Scorecard 46/1/13/0. Office half of Step 9 closed.

2. **Paper reporting (the live thread).** Step 8/9 is the results backbone (load shapes, peak-hour
   timing, the 2015→2022 COVID break, the 2030 WFH-band energy spread, office vs NECB-prototype
   EUI). Begin drafting the 3J results/methods sections from the validated campaign + the 8 report
   charts. (2J submission copy `readySubmission.md` is the style reference — see memory
   `project_2j_paper_writing`.) One paper caveat worth a sentence: the top office archetype EUI
   (216) pokes just above the 200 prototype ceiling; the gate is on the median (180, in-band) so
   it's non-blocking, but note it.

**Suggested opening line to the user:** "Step 8 is fully closed and the unified Step 9 (both
channels) is built — job 1055064 just needs its outputs collected + the two pipeline docs reframed
(see below). Want me to finish Step 9 first, then start the 3J results section?"

---

## 6. 🟢 DO THIS — wait on the autonomous chain, then pull + report the Step-9 scorecard

**The whole chain is ALREADY SUBMITTED and self-driving.** You do NOT need to submit anything on the
happy path — just wait for the watch to ping, then pull + parse + report. Submitted 2026-07-02:

| Job | Role | Gate | Log |
|---|---|---|---|
| **1058490** | office re-sim array (0-251, `--no-skip`) → `$SCRATCH/office` | — | `logs/8C_office_resim_1058490_*.out` |
| **1058661** | §8D re-agg (`run_aggregation.sh`) → `outputs_step8/agg/` | `afterok:1058490` | `logs/8D_agg_1058661.out` |
| **1058662** | Step-9 scorecard (`run_step9.sh`) → `outputs_step9/` | `afterok:1058661` | `logs/9_step9_1058662.out` |

**Watch:** model-free Monitor `b4xjufm32` (zero tokens) pings on Step-9 COMPLETED / chain-fail /
`DependencyNeverSatisfied`. If it's gone (session reset), re-arm an equivalent (poll `sacct -j 1058662
-X -n -o State` every ≥30 min; also `squeue -h -j 1058661,1058662 -o %E | grep -i Never`).
Progress at last check: **81/252 array tasks done, ~16/hr, 8-wide cap** → ETA ~5–11 h for the array +
~1 h agg + ~1 min step9 → results tonight/overnight.

**The Step-9 generator is ALREADY UPGRADED + STAGED** (`3rdJ_09_activityDrivenLoads_2split.py`, remote
md5 `f6ad1dc4…`): it now emits a **2J-style scorecard report** — verdict banner, PASS/WARN/INFO/FAIL
pills, an 11-gate bi-channel scorecard (doc §7 → `evaluate_gates()`), and **base64-embedded** figures
(self-contained HTML). The old "re-source office from peak/shape" edit is **NOT needed** — post-fix the
office channel varies by scenario in occupancy/mid-day, and gate **G8o** auto-tests that the 2030 bands
DIFFER. No script edit required on the happy path; if you do edit it, re-`scp` + re-verify md5 before
1058661 finishes (step9 is gated behind agg, so there's slack).

### WHEN THE WATCH PINGS — three cases

**CASE A · `CHAIN DONE: Step9 1058662 COMPLETED`** (happy path — hand mechanical bits to a
`model: sonnet` employee):
1. **On the cluster:** `tail -40 logs/9_step9_1058662.out` → read the console `SCORECARD: PASS n · WARN
   n · INFO n · FAIL n` line + each `G..` gate line (esp. **G8o**).
2. **Confirm G8o = PASS** (office 2030 bands non-degenerate). If G8o is **FAIL/WARN** → office still
   looks flat → the fix didn't fully take → **escalate to the user (Opus-worthy debug)** with the log.
3. **Locally (scp pull):** `scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step9_docs/outputs_step9/{step9_report.html,figures} "<local>/Leg2_2-split/Step9_docs/outputs_step9/"`
   (report is self-contained; figures optional). Open `step9_report.html`.
4. **Report to the user:** gate tally + G8o verdict + local path. That satisfies the "Step-9 validation
   report, both channels" ask.
5. **THEN (optional, ask first):** reframe the 2 pipeline docs (below) + start paper reporting.

**CASE B · `CHAIN STUCK: DependencyNeverSatisfied`** — an office cell (or agg) failed `afterok`, so the
chain will never fire. Recover:
1. `sacct -j 1058490 -X -n -o JobID,State | grep -v COMPLETED` → list the failed array indices.
2. `scancel 1058662 1058661` (clear the stuck dependents).
3. Re-run only the failed cells: `sbatch --array=<comma,idxs> Step8_docs/run_office_resim.sh` (it's
   `--no-skip`, overwrites). Verify with `squeue`.
4. When they drain, re-submit the chain: `sbatch --dependency=afterok:<newarray> …/run_aggregation.sh`
   → capture id → `sbatch --dependency=afterok:<aggid> …/run_step9.sh`. Re-arm the watch.

**CASE C · `CHAIN FAIL: … agg/step9 state=FAILED`** — `tail -60` the named log. Usual suspects: missing
dep in `envs/step4`, a path, or an OOM (bump `--mem`). If the cause is obvious + mechanical, fix +
re-submit that job (agg standalone, or step9 with `--dependency=afterok:1058661` if agg is fine). If
non-obvious → escalate to the user with the log tail.

---

### After Step 9 is in hand — reframe the 2 pipeline docs (archive predecessors first, HARD RULE #8)

STEP-9 boxes in `Leg2_2-split/3rdJ_00_2split_Occupancy_Pipeline_Overview.md` (~L112–117) +
`3rdJ_00_2split_Occupancy_Pipeline.md` (~L223–226): "office-only" → "both channels: residential (SHEU)
+ office (NECB) activity-driven end-use loads + EUI calibration; deep activity-resolved residential =
Leg-1 provenance, deep office = Leg-3 candidate." Then update `memory/project_step9_2split_status.md` +
`project_step8_office_wfh_bug.md` + this RESUME to DONE, and move to **paper reporting** (2J
`readySubmission.md` = style ref).

---

### Background — why Step 9 is bi-channel (still valid)

**Context (why Step 9 was rebuilt today):** the user pushed back that residential and office must
get **equal importance / attention / evaluation** (equal ≠ identical parameters — each channel keeps
its own physics: resid = MC + SHEU + REPLACE; office = deterministic + NECB + MODULATE). The 3J
pipeline docs had scoped Step 9 as *office-only* (residential Step 9 = Leg-1 / 2J). We agreed to
build a **unified, bi-channel Step 9 at aggregate depth** (presence→Lights/Equipment coupling +
aggregate site-EUI calibration, each channel vs its own benchmark), because that's the depth where
parity is genuinely achievable (office has no per-end-use benchmark like SHEU → can't go
activity-resolved without becoming the hand-wavy channel; deep activity-resolved office = a Leg-3
candidate). No re-simulation — it reads the existing §8D agg tables.

**Built today (all in `Leg2_2-split/Step9_docs/`, uploaded to the cluster upload tree):**
- `3rdJ_09_activityDrivenLoads_2split.md` — the bi-channel method+results doc (has an explicit
  "equal-treatment ledger" table answering the parity ask).
- `3rdJ_09_activityDrivenLoads_2split.py` — analysis script: reads `Step8_docs/outputs_step8/agg/`
  (agg_annual/peak/diurnal/meta) → `outputs_step9/{step9_eui_by_channel,step9_loadshape_peaks,
  step9_scenario_response,step9_longitudinal}.csv` + `figures/fig_{eui,diurnal,peakhour,scenario}_both.png`
  + `step9_report.html`.
- `run_step9.sh` — SLURM (`-p ps`, `-t 7-00:00:00`, py_compile + dep fast-fail), log
  `logs/9_step9_<JOBID>.out`.

> **⚠️ The old "job 1055064 ~80% done · re-source office from peak/shape" status is SUPERSEDED.**
> That run was built on the FLAT (buggy) office outputs, and its refinement plan assumed office was
> only annual-degenerate. Post-fix the office channel varies by scenario for real, and the generator
> now auto-evaluates it via gate **G8o** — no `build_scenario`/`build_longitudinal` re-source edit is
> needed. The current, live plan is **§6** above. What's still solid & unchanged: residential EUI /
> scenario / COVID-break, and the office load-shape hump — all re-emitted by the pending 1058662 run.

**The Step-9 deliverable when 1058662 lands:** `outputs_step9/` = 4 CSVs
(`step9_{eui_by_channel,loadshape_peaks,scenario_response,longitudinal}.csv`) + 4
`figures/fig_*_both.png` + **`step9_report.html`** (the 2J-style bi-channel scorecard — verdict,
pills, 11 gates, embedded figures). That HTML is the "Step-9 validation report, both channels" the
user asked for.

**Then (real next milestone): paper reporting.** Step 8/9 is the results backbone (load shapes,
peak-hour timing, 2015→2022 COVID break, 2030 WFH-band spread, both-channel EUI vs benchmark).
2J submission copy `readySubmission.md` is the style reference (memory `project_2j_paper_writing`).
