# Manager prompt — 3J Leg-2 (2-split) Step-8/9 cascade, continuation

**Paste this whole file as your first message in the new session.** You are the **manager**. You plan, delegate, verify, and log. You do not do mechanical work yourself.

---

## Your role and the non-negotiable rules

- **You are a MANAGER.** Every mechanical action — big-file scans, greps over campaign outputs, checksum sweeps, log parsing, edits to bulky files — goes to a **cheap-model employee** (`model: haiku` for trivial, `model: sonnet` for anything with judgement). Never scan a big file yourself.
- **Verify every employee report by independent re-derivation.** In the last session an error surfaced in essentially every employee report *and* in my own briefs. The discipline that caught them, every time:
  - Compare **sets, not counts** (an ID-set identity, not two totals that happen to match).
  - Compare **hashes, not sizes** (md5, never byte-length).
  - Re-derive from **the artifact's own columns**, never from a summary or a prior number — even when the number hits the plan's target exactly.
  - When you brief an employee with an "expected N", treat a mismatch as **your brief possibly being wrong**, not the employee's result. Four of my briefs were wrong last night from 2J-contaminated memory; each time the employee was right to refuse to conform.
- **Speed HPC hard rules (VERBATIM, in force):**
  - 🔴 **NEVER** run a blocking/interactive `srun`, bare `python`, or any computation on the login node (`speed-submit2`). **ALWAYS `sbatch`** — fire-and-forget. One violation = account suspension = all job progress lost.
  - 🔴 Every job submission **MUST** request minimum one-week walltime: `-t 7-00:00:00`.
  - 🔴 Submit every cluster command as a **single line**.
  - Login shell is **tcsh** → `2>/dev/null` is **invalid** there ("Ambiguous output redirect"). Do not redirect stderr in ssh-to-login-node commands.
  - **Archive the predecessor** of any file before editing it. **Never** overwrite pipeline output directories.
  - **Minimum monitoring frequency = 30 minutes.** Do not poll faster.
- **User directives in force:** *Don't ask questions — always decide, favoring the high-precision option.* Reserve `AskUserQuestion` only for choices the user alone owns (target journal, what to publish, scope). *Write a Progress Log entry for every step and every action.* Casual, short replies (≤100 words unless detail is requested).
- **If a change could alter publishable results, call it out clearly.**

---

## Governing document

`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg2_2-split\improvement\2J_to_3J_improvement_implementation.md`

This is the 4-task plan and the running Progress Log. **Append a Progress Log entry there for every action.** The cascade table near the end is your task list. Read the tail of its Progress Log first — it has the exact latest state.

---

## The two fixes this cascade propagates

1. **act30 recalibration (04T rake).** act30 was uncalibrated → physically-impossible **FLOATING** work slots (work with `hom30=0` AND `wrk30=0`). The new **04T** rake (runs *after* 04M) removes only FLOATING. It must **never** touch **TELEWORK** (work with `hom30=1` — legitimate, and the paper's core signal). Rake order: 04L (joint binary) → 04M (min-dwell smoother) → **04T** (activity).
2. **Multi-zone injection fix (`integration.py`).** Multi-zone buildings were losing ~(N−1)/N of equip/lighting energy. Fixed with per-zone carriers. Local fixed file md5 `6a92268be1f8dc3301df3bec80d6dd2e` (2,531 lines); predecessor md5 `2f3fda5b644655c7d9d38af1cf21fd62`. **Cluster copy was verified fixed and uploaded last session.**

---

## WHERE THINGS STAND (as of 2026-07-16 ~06:45)

**Step-8 campaign is RUNNING on verified-fresh inputs. Do NOT relaunch it — it is mandated to run EXACTLY ONCE.**

- **Job 1126073** — residential array (0–167, 168 tasks × 50 MC). At last check: tasks 0–115 COMPLETED, 116–119 RUNNING, 120–167 PENDING with reason `AssocGrpCpuLimit` (account concurrent-CPU throttle — **normal**, not an error).
- **Job 1126074** — office array (0–251, 252 tasks). Fully PENDING, `AssocGrpCpuLimit`. Will start automatically as residential frees CPUs. **This is expected** — office had not started yet.
- Inputs were verified fresh before this launch. A **first launch (1126045/1126046) was cancelled** because it ran on stale June-derived historical schedules; the 2005/2010/2015 schedules were regenerated (8A → 2,883 HH / 138,384 rows, gates PASS), re-uploaded (6/6 md5 match), the partial run archived, then relaunched as 1126073/1126074.
- **The Monitor from the previous session does NOT carry into this session.** Your first action is to re-check job state (`squeue`/`sacct`) and, if still running, re-arm a Monitor that polls **every 30 min** and emits only on terminal state or failures.

### Numbers you must hold (corrected — do not regress to the 2J values)
- **Frame:** post-exclusion **23,150** HH / 29,538 rows / 30,273 agents / 735 excluded. (NOT 23,211/29,599/674. 23,882 = pre-exclusion SIM_HH_ID count, correct only at that stage.)
- **Historical stock** (2005/2010/2015 schedule generator, `3rdJ_08A_...py:495`) is built from the **2,883 real 2022 GSS respondents** — expect **2,883**, NOT 23,150.
- **Step-8 val baseline:** 46P / 1W / 13I / 0F. Gate 4.9 **WARN is acceptable** (per ERV v3).
- **Step-9 baseline:** 10P / 1W / 0F. Watch **G8o** (WFH modulation) and the **office EUI band**.

---

## YOUR TASK LIST (in order)

### 1. Re-establish monitoring (immediately)
Single-line `ssh speed-submit2 "squeue -u o_iseri ...; sacct -j 1126073 -X --format=State | sort | uniq -c; sacct -j 1126074 ..."` (no stderr redirect). If running, re-arm a 30-min Monitor. Log it.

### 2. When the campaign reaches terminal state — Step-8 aggregation
- Confirm **all** tasks COMPLETED (not just "no longer running"). Check for CANCELLED/FAILED/TIMEOUT via `sacct`. Read a **successful** task's log to confirm content, not just exit code (last time a stale run had exit-0 tasks).
- `sbatch` `Step8_docs/3rdJ_08_simulation_2split_agg.py` (single-line, `-t 7-00:00:00`). Only `to_csv` is at `:538` (AGG_FILES dict). It writes agg_annual/diurnal/meta/peak; it does **NOT** write `agg_enduse_annual.csv`.

### 3. Step-8 validation
- `sbatch` `Step8_docs/3rdJ_08_simulation_2split_val.py`. Expect **46P/1W/13I/0F**, gate 4.9 WARN OK.
- `agg_enduse_annual.csv` is produced separately by `investigation/extract_enduse_annual.py`; the validator degrades those to INFO if absent (`:1465-1467`). Optionally run that extractor post-campaign to populate the INFO gates.

### 4. Task-2 magnitude check (the point of the whole injection fix)
Delegate a **sonnet** employee: compare `equip_kWh` / `lights_kWh` by `arch`, **fresh `agg_annual.csv`** vs **`archive/agg.20260706_pre_actv2/agg_annual.csv`**. **Expected:** MidRise / HighRise / OtherDwelling equipment-electricity **up by ~zone-count factor**; DetachedHouse **~1.0×** (single-zone, unaffected). If DetachedHouse moved materially, something is wrong — investigate before proceeding. **This could alter publishable results — call out the magnitude explicitly.**

### 5. Step-9 re-run
- `sbatch` `Step9_docs/3rdJ_09_activityDrivenLoads_2split.py` (verify exact path). Expect **10P/1W/0F**. Watch **G8o** and **office EUI band**.

### 6. Acceptance note
- Append to `investigation/2split_results_acceptance_review.md`, **superseding** the 2026-07-02 PAPER-READY verdict. State the new scorecards, the Task-2 magnitude delta, and any residual caveats.

### 7. (Non-blocking, out of scope) tickets to leave filed, not fixed
- **G4 pooled-strata defect:** `investigation/TICKET_G4_pooled_strata_defect.md` — already filed. The Step-4 G4 FAIL after 04T is a **Simpson's-paradox composition artifact**, not a regression; per-stratum fit *improves* (weekday 14.5→0.3pp, Sat 8.0→0.02, Sun 7.0→0.00). Do **not** fix mid-cascade (would make before/after scorecards incomparable).
- **Cross-era pairing ticket:** the "paired design" claim (`3rdJ_08B_run_paired_mc.py:196`) does **not** hold across eras — historical scenarios draw from 2,883 HH, 2022/2030 from 23,150. Same seed, different pools. Pairing is valid 2022↔2030 bands only, not along the 2005→2030 trend. Pre-existing (June had the same structure), out of scope. Verify against archived June manifests, then file — do not touch the pipeline.

---

## Key file map (verify paths before acting; don't trust from memory)

| What | Path (under `Leg2_2-split/`) |
|---|---|
| Historical schedule generator | `Step8_docs/3rdJ_08A_gen_historical_schedules.py` (stock = real 2022 resp., `:495`; AUG input `:53-54`) |
| Paired MC runner | `Step8_docs/3rdJ_08B_run_paired_mc.py` (`:196` paired-design claim — false across eras) |
| Scenario/schedule map | `Step8_docs/eSim_bem_utils_3J/main.py` (SCHEDULE_FILE_MAP `:94-98`, COMPARATIVE_SCENARIOS `:50-53`, 7 scenarios) |
| Multi-zone fix | `Step8_docs/eSim_bem_utils_3J/integration.py` (fixed md5 `6a92268...`) |
| Step-8 agg | `Step8_docs/3rdJ_08_simulation_2split_agg.py` (`to_csv` `:538`) |
| Step-8 val | `Step8_docs/3rdJ_08_simulation_2split_val.py` (enduse load `:62`, INFO-degrade `:1465-1467`) |
| Enduse extractor | `investigation/extract_enduse_annual.py` |
| Baseline agg (pre-fix) | `archive/agg.20260706_pre_actv2/agg_annual.csv` (md5-verified) |

Speed scratch base: `/speed-scratch/o_iseri/step8_2split/` (upload tree under `upload/3J_docs_occ_nTemp/Leg2_2-split/`; campaign outputs in `campaign/` + `office/`; logs in `logs/`).

---

## The one thing to internalize

The recurring root cause of last night's ~5 errors was **reasoning from one end of a chain without walking the other** — wrong comparison reference, wrong producer script, unverified inputs I didn't know existed. Before you trust any number: find the artifact that produced it and re-derive from its own columns. Before you launch anything: inventory every input it reads and hash-verify each one is the fresh version.
