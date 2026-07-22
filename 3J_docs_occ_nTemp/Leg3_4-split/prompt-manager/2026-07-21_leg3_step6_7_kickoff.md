# MANAGER KICKOFF PROMPT — 3J Leg-3 (4-split) — CONTINUE AT STEP 6 → STEP 7
### Paste this whole file into a fresh manager session (Opus). Authored 2026-07-21 by the Step-5-closeout manager session. Supersedes `2026-07-20_leg3_step5_kickoff.md` for the *entry point* only (all prior rules still apply verbatim). Covers finishing **Step 6 (forecasting) AND Step 7 (BEM integration)** — Step 6 must fully validate before Step 7 consumes it.

---

You are the **manager (Agent1, Opus)** for the 3rd-Journal **Leg-3 four-channel pipeline** (Residential + Office + **Retail** + **Hotel**). You plan, debug, review, and author employee prompts; you do **not** execute multi-step implementation yourself. Employees (Sonnet; Haiku for mechanical/monitoring/scp work) execute one task at a time from the step runbooks and append a Progress Log entry. Every employee prompt must state: *"You are the employee. Execute the task below and append a Progress Log entry on completion."*

**The runbooks under `Leg3_4-split/Step{6,7}_docs/` are the single source of truth — execute as written, do not redesign.** If a decision-level question surfaces, stop and ask the user; never decide silently.

---

## What is already DONE (do not redo)

- **Steps 1–4 COMPLETE** (design frozen 2026-07-02; Steps 1–3 done 2026-07-19; **Step 4 CLOSED 2026-07-20**, seed-3 locked pool, 149P/16W/1F, sole FAIL = OW5 inherited/documented).
- **STEP 5 CLOSED 2026-07-21 — LOCAL census linkage.** Winner chain **MIN_POOL=15** (pareto-optimal over the sweep: 11→4F, 20→4F, 30→5F+W1 break). Final scorecard **32 PASS / 4 WARN / 3 FAIL**. Frame of record: `Full_Schedules.csv` = **30,273 rows**, `excluded_pids.csv` = **771**. Aggregated products present locally: `Step5_docs/outputs_step5/3rdJ_25CEN_aug_Full_Aggregated{,_excl}.csv`.
  - **The 3 residual FAILs are ACCEPTED AS DOCUMENTED (manager decision 2026-07-21 — no gate relaxed, none redefined, matcher + MIN_POOL=15 untouched).** Verified mechanisms + approved paper caveats live in `Step5_docs/outputs_step5/investigation/INVESTIGATION_3fails_findings.md` and the closure Progress-Log entry in `3rdJ_05_censusLinkage_4split_val.md`:
    1. **Gate 2.2 AT_HOME WD** (3.66 pp, 6/96 slots) — a **within-cell property of the Step-4 pool** (synthetic diaries carry lower daytime home-presence than observed diaries in the *same* employed working-age cells; the 94%-employed census frame surfaces what the 54%-employed pool aggregate hides). Out of reach of any Step-5 matcher lever; a real fix would be **Step-4-side conditional AT_HOME calibration (a separate retrain decision — NOT in scope for Steps 6/7).**
    2. **Gate R1 AT_RETAIL** (4.796 pp, 2005-d2) — not noise (null p ≤ 0.012); the deviation IS the census demographic reweighting the matcher exists to perform. R1 reference deliberately **NOT redefined** (avoid gate-shopping). Note the related WARN **R2a**: midday weekday retail 0.025 vs empirical band 0.06–0.10 is **pool-bounded** (GSS-diary pool itself = 0.047) — a single-archetype retail-v1 magnitude limitation.
    3. **Gate 0.1 PR=6 Territories** — genuine GSS frame gap (24 agents, 0.079%, all Tier-3, national-proportional donors, verified exact). Definitionally unfixable.
  - **Carry-forward for Steps 6/7:** the retail channel is **single-archetype v1** (no respondent-level retail archetype) and sits **low in absolute midday magnitude** — this is exactly why Step 6's retail lever is **amplitude-only, post-hoc** and Step 7 injects retail as a **peak-normalized shape × 0.95 NECB fraction**, never a raw fraction. Do not try to "lift" retail magnitude inside the matcher or the diaries — it is a documented v1 property.

---

## STEP 6 — Longitudinal Forecasting 2005–2030 (execute FIRST, must reach 0 FAIL before Step 7)

**Runbook:** `Step6_docs/3rdJ_06_longitudinalForecasting_4split.md` + `..._val.md`. **The Leg-3 scripts do NOT exist yet** — only the two runbook `.md`. Build them by **porting the Leg-2 Step-6 file set** and applying the Leg-3 deltas (below). Two tracks, different compute:

### Track A — GSS Transformer forecasting (**CLUSTER, GPU `pg`** — cluster discipline REACTIVATES)
Fork bases (Leg-2, use the live non-archived versions):
- `Leg2_2-split/Step6_docs/3rdJ_06_longitudinalForecasting_2split.py` (+ `_val.py`)
- `assemble_scenario_2030_2split.py`, `calibrate_weekday_work_2split.py`, `3rdJ_06_calibrate_C_activity_weekend_2split.py`, `mutex_check_backcast_2split.py`, `verify_backcast_metric_2split.py`, `profile_forecast_weekday_2split.py`, `characterize_bias_2split.py`, `3rdJ_06_forecast_rake_2split.py` (present; port only what the runbook's module list calls for).
- **Model import (LOCKED):** `3rdJ_04B_model_4split.py::JSeriesHybrid4Split` — **3-head**.

Leg-3 deltas (everything else verbatim Leg-2):
- **DRIFT_MATRIX gains the AT_RETAIL axis** (14 activities × 3 DDAY_STRATA × archetypes × {AT_HOME, AT_WORK, AT_RETAIL}); COVID `_1522` triple-signal check = AT_HOME ≥ +5 pp **and** AT_WORK ↓ **and** AT_RETAIL ↓ must co-occur.
- Loss **fixed α 1.0 : 0.5 : 0.3 + PCGrad** (NOT Leg-2 UW); retail `pos_weight=49` + −ln 49 decode shift preserved through every fine-tune stage.
- **Train on the RAW (pre-rake) Step-4 pool, never the raked/locked pool** (OD-1). Backcast reference = the locked (raked) pool, comparison only.
- 6F **2022 backcast gate = profile metric** (shape-JS + level-MAD, NOT raw flattened-binary JS — it saturates on the ~2% retail channel): AT_HOME ±2 pp, AT_WORK ±3 pp, **AT_RETAIL ±1.5 pp level / MAD < 0.10**, WFH_RATE ±5 pp. Backcast temperature = deliverable settings (T 0.7 + nucleus 0.9 + min-dwell), **never greedy T=0**.
- 🔴 **Self-pairing bug (the Leg-2 Step6Dataset copier bug):** never `src == tgt` — an identity autoencoder produced three identical bands and backcast JS = −0.0000 was the tell. Replicate the 04C KNN cross-day pairing.

### Track B — Hotel SARIMA (**LOCAL**, statsmodels, seconds — non-GSS, no cluster)
New file `3rdJ_06_hotel_sarima_4split.py`: fit on **pre-COVID 2005–2019**, select by BIC/AICc (expect SARIMA(1,1,1)(1,1,1)₁₂), Ljung-Box whiteness, **freeze orders**; re-estimate on full 2005–2022 with **COVID pulse + permanent level-shift** intervention terms (+ AB `D_splice` if a splice level-shift is detected). Backcast gate: 2015–2019 QC+AB **MAE < 0.05**, 2020-04 dip recovered without overshoot. Then 6J: 2030 monthly path + bands **Low 0.92 / Central 1.00 / High 1.05** (tilts AB low 0.90, QC high 1.07); emit `hotel_multiplier_2030.csv` + `hotel_multiplier_lookup.csv`; s(t) = dr_L3-05 48-slot table (plateau 1.00 22:00–06:00; trough 0.200 wd / 0.308 we).

### Retail lever + calibration/cleanup (6G/6H)
- **Retail lever = post-hoc amplitude multiplier** (relative to 2022 = 1.00): Plateau/Default **0.97** · Continued-Shift **0.90** · In-Store-Renaissance **1.05**; multiplies `at_retail_fraction_2030(t)` **before** Step-7 peak-normalization. Optional QC-Sunday deregulated variant = an extra file, not a 4th band.
- **6H cleanup:** 3-way mutex arbitration {home,work,retail} + `3rdJ_04M_mindwell_4split.py`; **NO 04L rake on 2030** (no observed 2030 marginals — circular); retail cap = observed-2022 profile × lever (target-anchored, never delta-subtraction).
- 🔴 **Mutex guard inside EVERY calibration stage** (the 2026-07-17 Leg-2 mutex bug: calibration-C weekend min-dwell re-raised `hom30` on `wrk30==1` slots → 4,280 impossible cells forced a 72-task re-sim). (a) Fork from the **FIXED** calibration-C (the archived `*_pre_mutexfix` is the WRONG base); (b) hard assertion after every stage that writes any channel: `(hom∧wrk)=(hom∧ret)=(wrk∧ret)=0` — abort, never warn; (c) any smoother must check the other two channels before raising a slot.
- **Canonical deliverable = `2030_synthetic_diaries_4split_calibrated_mindwell_C.csv`.** Move all superseded variants (`_BAK_*`, `.preRake_*`, non-`_C`) to `outputs_step6/archive_pre_*/` at write time; **record the `_C` MD5 in the Progress Log** at sign-off.

### Step-6 CLI + validation
`--smoke` locally end-to-end (tiny epochs) → hotel script locally in full → **cluster: `sbatch slurm_06_4split.sh` (`-p pg --gres=gpu:1 -t 7-00:00:00`, sbatch ONLY, no polling, read `.out` after)** → `3rdJ_06_..._val.py` target **0 FAIL**. Band checks: office WFH monotone (fully>hybrid>cons), retail lever exact (0.90/0.97/1.05), hotel monotone (low<central<high).

**🛑 DECISION FORK — the ONLY user checkpoint in the 6→7 run: confirm the 2030 scenario matrix.** Once Step 6 validates at 0 FAIL, stop and ask the user to confirm the **2030 scenario matrix** (runbook default = 3 aligned bundles + baseline, NOT the full 27-cross; Step-7 §SCENARIO MATRIX) — this sets how many product sets Step 7/8 build. Also confirm the AB hotel-series fallback if only the truncated 2010–2022 AB series shipped. **After the matrix is confirmed, Step 6 chains straight into Step 7 with no further closure checkpoint** — do not pause to report Step-6 completion separately; the scenario answer is the go.

---

## STEP 7 — Four-Channel BEM Integration (execute AFTER Step 6 validates — **LOCAL** product build)

**Runbook:** `Step7_docs/3rdJ_07_bemIntegration_4split.md` + `..._val.md`. Builds the four per-channel schedule **products** Step 8 consumes. Injection asymmetry: **Residential = REPLACE; Office / Retail / Hotel = MODULATE** (densities never scaled).

Fork bases (fork the **FIXED** Leg-2 versions, NOT their archived predecessors):
- `3rdJ_07_aug_to_bem_4split.py` ← `Leg2_2-split/Step7_docs/3rdJ_07_aug_to_bem_2split.py` **post-2026-07-18** (D2030 default hardened to `_C`; the `.20260718_preD2030harden` predecessor is the WRONG base).
- `3rdJ_07_bemIntegration_4split_val.py` ← `Leg2_2-split/Step7_docs/3rdJ_07_bemIntegration_2split_val.py`.
- `commercial_integration.py` (**NEW** — extend `inject_office_schedules()` → `inject_mixed_use(idf, channels, building_meta)`): residential branch forks `eSim_bem_utils/integration.py` **post-multizone-fix** (md5 `6a92268be1f8dc3301df3bec80d6dd2e`); office branch forks the post-2026-07-02 `office_integration.py` (v24.2 zone-field + People-field fixes in).

Products (all under `outputs_step7/`): (1) residential `BEM_Schedules_4split_{2022,2030_<band>}.csv` (13-col); (2) office `office_presence_multiplier_{2022,2030}.csv` (7-col); (3) **retail (NEW)** `retail_presence_multiplier_*` (`multiplier = 0.95 × peak-normalized shape`, staff-shoulder slots keep baseline, Sunday differs QC vs AB); (4) **hotel (NEW)** `hotel_schedule_multiplier_*` (`s(t) × monthly_rate`, 12 monthly blocks in one annual `Schedule:Compact` per guest-room Space).

🔴 **Non-negotiable Step-7 gates (all Leg-2 hard-learned):**
- **H8 input-mutex hard gate** — 0 slots with >1 of {hom30,wrk30,ret30}=1 in BOTH the 2022 stock AND the 2030 `_C` diaries, asserted **before** any product is built (Leg-2 had no such check → the 4,280-cell cascade).
- **H6 `_C`-only** — 2030 source must be the `_C` file; hard-fail on a non-`_C` default.
- **Wiring assertion (the byte-identical-scenarios bug):** every schedule the injector claims to modulate is actually referenced by the correct IDF field (`Number_of_People_Schedule_Name`, not `Schedule_Name`) **and** the modulated series differs from baseline where multiplier ≠ 1 — assertion failure = abort, no sbatch (in Leg-2 all 7 office scenarios simulated byte-identical from exactly this).
- **Clock-roll discipline (H9):** all GSS-derived 48-slot arrays are 04:00-origin → apply the `np.roll(+4h)` diary→clock roll to residential, office AND retail; the **hotel s(t) is already clock-indexed → NO roll** (assert the overnight plateau lands 22:00–06:00). A mis-rolled channel = peak at an absurd clock hour (the 2J "00h peak" class of bug).
- **Tag-2 dispatch is exact `Tag 2 == "<literal>"`, not substring** (runbook routing table).
- **Frame counts from the Leg-3 Step-5 record** (residential stock = the `Full_Aggregated` above) — never assume a Leg-2 constant.

Step-7 CLI (local, in order): `--audit` → `--year 2022` → `--year 2030 --bundle {cons,central,opt} [--sens <channel>]` → `3rdJ_07_bemIntegration_4split_val.py` (target 0 FAIL). MD5-compare the office product against Leg-2's as an insulation check (near-identical expected).

---

## Global rules (full text in CLAUDE.md + the runbooks) — in force

- **🔴 Cluster (Step-6 Track A GPU jobs — REACTIVATED):** `sbatch` ONLY, **never** blocking/interactive `srun`, **no bare python on `speed-submit2`** (this includes one-liners and dir scans — account-suspension risk, flagged three times), single-line commands, **`-t 7-00:00:00` on EVERY job** (no short caps ever), ≥30-min monitoring spacing, **no polling loops** (submit → capture job id → read `.out` later; one-shot `squeue`/`sacct`/`tail` OK). Login shell is tcsh (no `2>/dev/null`/`2>&1`); wrap remote multi-command work in `ssh speed bash -s <<'REMOTE' … REMOTE`. Step 6 Track B (hotel) + all of Step 7 run **locally** (`py -3 -X utf8`).
- **Cost:** poll/peek/scp/log-tail/**big-file scan = Haiku/Sonnet employees, never Opus**. Never scan the ~399 MB pool or the 2030 diaries in your own context — write the extraction script, hand it to a cheap employee, get back a small table.
- **Archive the predecessor** before editing any file (`archive/<name>.<date>_pre<Fix>.<ext>`); new outputs to NEW dirs, never overwrite a pipeline output dir; **fork from FIXED bases, not archived predecessors** (calibration-C, D2030-harden, multizone-fix, office-field-fix — all called out above).
- **Verify claims from the artifact, not the log** — re-derive every load-bearing number from the file's own columns; compare household-ID **sets**, not counts.
- **Never relax a gate threshold to clear a FAIL** — document with evidence + reclassify (the Step-5 3-FAIL closeout is the template).
- **User checkpoints:** decision-level trade-offs → stop and ask (the Step-6→7 scenario-matrix fork above is mandatory). Append-only Progress Logs; non-closure discipline ("Step N NOT done") until the validator signs off at 0 FAIL (or documented WARN/INFO). **Update the auto-memory Leg-3 status entries (`project_3j_leg3_step5_status.md` is closed; write the Step-6 then Step-7 status) at each step closure.**

---

## First actions for this session

1. Read both Step-6 runbooks + both Step-7 runbooks end-to-end, and the Leg-2 Step-6/Step-7 fork bases (main `.py` + `_val.py` + `assemble`/`calibrate`/`mutex_check`/`verify_backcast` modules), plus the Leg-2 Step-6 val doc (inherited gate thresholds + the calibration-C mutex-fix context).
2. Confirm inputs: the **RAW (pre-rake) Step-4 pool** location for training (Track A trains on raw — confirm it exists on the cluster; the *locked/raked* pool is backcast-reference only), the hotel canonical monthly series `0_Occupancy/external/hotel_occupancy_monthly.csv`, and the Step-5 `Full_Aggregated{,_excl}.csv` (Step-7 residential input, present locally). Delegate any big-file existence/schema peeks to a cheap employee.
3. **Author the Step-6 build employee prompt first** (Track A port + Leg-3 deltas, with the self-pairing + mutex + no-2030-rake + `_C`-hygiene disciplines explicit), then the Track-B hotel prompt (local), then the run/validate prompts. Track A's training goes to the cluster via `sbatch` — one submit, capture job id, read `.out` later (no polling).
4. When Step 6 validates at 0 FAIL: append the Step-6 Progress Log with the **`_C` MD5 + re-derived band checks**, update auto-memory, and **stop only at the scenario-matrix decision fork** to get the user's confirmation. That answer is the go — **do not add a separate Step-6-completion report; 6 chains straight into 7.**
5. As soon as the matrix is confirmed, author the Step-7 build + run/validate prompts (local) directly, enforcing the H8 mutex / wiring / clock-roll / `_C` gates in each. Close Step 7 at 0 FAIL, update auto-memory, report — **do not advance to Step 8** without user go.

Bonne exécution.
