# V3 - plumbing check (V3b) and seed replicates (V3a): design and runs

Task doc:  `writing/implementation/3J_IMP_execution_2026-09-22.md` section "V3"; plan Section 7a.
Status:    (2026-09-25) V3a ran LOCALLY on the P10R arm, INTERRUPTED at 25/40 by the RAM guard, see Section 11.
           Earlier: V3b IN PROGRESS - smoke 1342424 running; V3b array 1342426 (afterok smoke) and checker 1342427
           (afterany array) pending. Squeue at submission: 1J 30 CPUs running, 3J 1 running.
           V3a DESIGNED, NOT SUBMITTED (manager hold, 2026-09-22: input products are being rebuilt by P10R).
Code:      `writing/implementation/IMP/scripts/V3/` (mirrored on Speed, see Section 6).
Written:   2026-09-22. Sections 3.3-3.5 (tolerance, verdict rules, predictions) were written BEFORE any
           V3 simulation ran; the only thing run before them was the static (no-simulation) pre-check of 3.2.

---

## 1. Feasibility (execution-doc step 1)

- **EnergyPlus on Speed = same build as the frozen arm.** Speed runs EnergyPlus through the Singularity
  image `/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`, binary
  `/EnergyPlus-24.2.0-94a887817b-Linux-Ubuntu22.04-x86_64/energyplus` (wrapper
  `/speed-scratch/o_iseri/ep_wrappers/energyplus`; the same constants are in
  `Leg3_4-split/Step8_docs/3rdJ_08P_probe_driver.py:88-89`, used by 3J arms A-H and R). The frozen
  deliverable ran `24.2.0`, build `94a887817b` (`campaign_local_deliverable/*/manifest.json`
  `energyplus_build`). **No version gap. Platform gap only: win32 (frozen) vs linux (Speed).** Both V3b
  arms that are compared run on Speed; the win32-vs-linux difference is measured and reported (U vs frozen),
  never gated.
- Python on Speed: `/speed-scratch/o_iseri/envs/step4/bin/python` (3.10, eppy + pandas; the env arms A-H used).
  IDD: the local `C:\EnergyPlusV24-2-0\Energy+.idd` is uploaded to `repo/Energy+.idd` and used for all eppy work.
- The injector (`eSim/eSim_bem_utils/commercial_integration.py`) and the Step-9H resize scripts ran on Linux
  before (arms A-H, R). 1J/2J submit EnergyPlus the same way (Singularity 24.2.0 image); 3J's own route was reused.
- **Per-cell run time.** Local win32, 6 parallel workers (`Step8_docs/campaign_local_v2/_campaign_run.log`):
  Tall/MTL 7.9-9.1 min, Tall/CLG 8.7-10.8 min, SuperTall/MTL 15.4-15.9 min, SuperTall/CLG 15.4-19.0 min.
  Speed, arm H (sacct, job 1171496, 4 CPUs, injection included): 24 min to 1 h 14 min, most 40-49 min.
  Budget used below: about 45 min per cell on 1 CPU.

## 2. What I found before designing (read these first)

**F-V3-1 (important for P3 and the manuscript).** The frozen deliverable was injected with the
**pre-T9-9** injector behaviour: in office, retail and hotel-guest-room Spaces, LIGHTS and
ELECTRICEQUIPMENT carry the channel's **occupancy** schedule, not their own code schedules. Evidence:
`Leg3_4-split/Step8_docs/campaign_local_deliverable/B_central__Tall__MTL/injected_resized.idf` lines
81833-82301 (`OpenOffice Lights`, `Retail Entry Lights`, `OpenOffice Elec Equip`, ... all `Schedule Name =
MXU_Office_People_...` / `MXU_Retail_People_...`); `MXU_Office_People_*` is referenced 19 times
(1 definition + 6 People + 6 Lights + 6 Equipment). The injector itself documents this as defect S9D-8
(`eSim/eSim_bem_utils/commercial_integration.py:386-395`: "office equipment energy fell 59 % and lighting
45 %"), and `preserve_load_standby_floor=False` "reproduces the pre-fix behaviour EXACTLY"
(`:413-414`). The frozen campaign (`campaign_local_v2/campaign_cf69d508`, driver md5 `04a2a9be`) ran
before T9-9 existed (its logs carry no `[arm]` line). V2-E5 (`improvements/v2/V2-E5_PREREGISTRATION.md`
"Method") built the deliverable from exactly that base arm.
- Manuscript §3.6 (`writing/fullSet/readySubmission.md:440-447`) says retail lighting follows opening
  hours, retail plug load stays on the NECB baseline, and "minimum lighting and baseline plug floors are
  enforced". **The frozen IDF does not do this.** (For the manager: a text-vs-model mismatch.)
- Consequence for P3 (`IMP/P3_code_schedule_comparison.md` verdict, bullet 4 "channels whose lighting and
  equipment follow occupancy"): the code-schedule vs survey differences in office and retail energy mix two
  things - the survey timing, and the switch of lights/equipment from their code schedules to an occupancy
  schedule. **V3b's "U vs R" comparison measures the second part alone, with code occupancy** (Section 3.1).

**F-V3-2.** The frozen injector (`INJ_HASH cf69d508` = md5 prefix of the injector file then) is no longer
on disk; the live injector is `233932d7...` and the live V2-D9 converter is `fca94812...` (registered:
`28714c43...`, `V2-G1_FROZEN_DELIVERABLE.md` "Code hashes"). Tested rather than assumed: the static
pre-check (3.2) shows the live toolchain rebuilds the frozen `Default_NECB`, `Y2022` and `B_central`
(seed 42) IDFs **object-for-object** (Tall/MTL and SuperTall/CLG). V3 therefore uses the live code.

**F-V3-3 (for P10).** Frozen `B_central` cells read `office_presence_multiplier_2030_BAK_2026-08-02.csv`
(md5 `1536c98c...`) and `retail_presence_multiplier_2030_central_BAK_2026-08-02.csv` (`cf8721c6...`)
(`campaign_local_deliverable/B_central__Tall__MTL/manifest.json` `INPUTS_HASH_DETAIL`). The live files in
`Step7_docs/outputs_step7/` (`575d17e5...`, `11414644...`) were rebuilt later (FINDING 6/7) and were
never simulated in the frozen arm. `Y2022` inputs match the live files.

## 3. V3b design - plumbing check (pre-registered)

### 3.1 Why the reference is R, not the uninjected run U

Sending code schedules through the injector cannot reproduce the uninjected run U, **by construction**:
(a) the injection contract (F-V3-1) moves commercial LIGHTS/EQUIPMENT onto the occupancy schedule;
(b) residential REPLACE writes an integer household size per apartment, while the code carrier is a
density (0.040015 person/m2) times area. So the plumbing question is split in two:

| Comparison | Question | Status |
|---|---|---|
| **N vs R** | Does the injection code do exactly what its contract says, and nothing else? | **GATE** |
| X vs R | Would the gate see a real schedule error? (negative control) | must FAIL |
| U2 vs U | How much do two identical runs differ on Speed? (noise floor) | must be <= TOL/10 |
| U vs R | How much does the contract itself change energy with code schedules? | reported |
| N vs U | Whole injection-path effect with code schedules | reported |
| U vs frozen | Cross-platform (linux Speed vs win32 frozen), same IDF, same E+ build | reported |

Arms (per building-city cell: Tall/SuperTall x MTL/CLG; 5 arms x 4 cells = 20 tasks, 1 CPU each):

| Arm | IDF | Built by |
|---|---|---|
| U | frozen `campaign_local_deliverable/Default_NECB__<b>__<c>/injected_resized.idf`, byte copy | - |
| U2 | same as U, second run | - |
| R | U with the contract applied by hand rule: LIGHTS/ELECTRICEQUIPMENT of the 6 office, 4 retail, 3 guest-room Space types re-pointed to the schedule their own People object carries (`NECB-A-Occupancy`; `NECB-C-Occupancy` for retail); apartment carrier set to 0 people and one People object per apartment Space with 2 people on the carrier's own schedules | `v3_build_R.py` (text edit, no injector code) |
| N | base Leg-2 IDF -> injector (deliverable flags) fed the **code schedules in the four product formats** -> ensure-outputs -> V2-D9 -> V2-D10 resize | `v3_lib.build_injected` + `v3_fixtures.py` |
| X | N with the office weekday schedule rolled +3 h | same, `v3_office_necb_shift3h.csv` |

Fixtures (`scripts/V3/fixtures/`, values READ from the four frozen Default_NECB IDFs, asserted identical):
office `NECB-A-Occupancy` (weekday; Saturday = Sunday = 0), retail `NECB-C-Occupancy` (weekday / Saturday /
Sunday+holidays, 48 half-hour slots), hotel `NECB-A-Occupancy` for all 12 months, residential pool of 60
identical households (household size 2, `NECB-A-Occupancy`, activity 130 W = `NECB-Activity`). The product
formats represent these schedules exactly (Saturday = Sunday in NECB-A; NECB-C already has the injector's
3-day-type structure) - checked, not assumed, by 3.2. File md5s: `fixtures/fixtures_manifest.json`.

### 3.2 Static pre-check (local, no simulation) - `scripts/V3/v3_precheck_local.py`

`v3_static.py` compares two IDFs object by object, with every schedule reference replaced by the schedule's
expanded values (12 months x 12 day types x 48 half-hours; Output objects and object order ignored; IDD
defaults written out = blank). Result, Tall/MTL (`data/V3/precheck_Tall_MTL.json`):

| Check | Objects differing | Meaning |
|---|---|---|
| live toolchain, no channels vs frozen Default_NECB | 0 / 0 | rebuild is exact |
| N vs R | 0 / 0 | the injection does exactly the contract, and nothing else |
| X vs R | 18 / 18 | exactly the 6 office People + 6 Lights + 6 Equipment objects (the control is visible) |
| Y2022 seed 42 rebuild vs frozen Y2022 | 0 / 0 | frozen injected IDFs reproducible |
| B_central seed 42 (BAK products) vs frozen B_central | 0 / 0 | same |

SuperTall/CLG (`data/V3/precheck_SuperTall_CLG.json`): identical outcome on all five checks (0/0, 0/0,
18/18, 0/0, 0/0).
Every Speed N/X task repeats "N vs R" statically and records it in its manifest (`static_vs_R`).

So the IDFs are equal before simulation; the energy-level gate below tests that EnergyPlus agrees (object
order, schedule-name and object-count differences must not change results beyond float noise).

### 3.3 PRE-REGISTERED TOLERANCE (written before any simulation)

A comparison A vs B PASSES iff, for **every** column of `hourly_meters.csv` (15 meters) and
`channel_hourly.csv` (36 channel x end-use series), with identical shape and column names:
- annual: `|sum A - sum B| / max(|sum B|, 1e-9 x site_J(B))` **<= 1e-6**
- hourly: `max_t |A_t - B_t| / max(max_t |B_t|, 1e-9 x peak_site(B))` **<= 1e-4**

(site = Electricity:Facility + NaturalGas:Facility.) Justification: EnergyPlus with one binary on one
platform is deterministic, so U2 vs U is expected to be exactly 0; the only legitimate N-vs-R differences are
floating-point summation order (objects appear in a different order and under different names), which is
of order 1e-12 to 1e-9 relative. 1e-6 annual / 1e-4 hourly sits 3+ orders above that and 3+ orders below
any schedule effect (the checker selftest shows the Y2022-vs-Default difference is 0.66 annual, 0.83 hourly).
**The tolerance is justified only if the measured noise floor (U2 vs U) is <= TOL/10**; otherwise V3b is
NOT_EVALUABLE, not PASS.

### 3.4 Verdict rules

Per cell: noise (U2 vs U) must be <= TOL/10; control (X vs R) must FAIL ("FIRED"); gate (N vs R) PASS/FAIL.
Overall PASS iff all 4 cells complete, noise ok, control FIRED, gate PASS 4/4. Any missing or failed run,
noise above TOL/10, or a control that does not fire -> NOT_EVALUABLE. Checker exit code: 0 PASS, 1 FAIL,
2 NOT_EVALUABLE, 3 checker crashed (not a verdict). The summary keeps DID_NOT_RUN / RAN_NOT_FIRED / FIRED
apart for the control.

### 3.5 Predictions (pre-registered)

- P-b1: gate PASS in 4/4 cells, worst metrics below 1e-9 (static identity says N and R are the same model).
- P-b2: noise floor exactly 0 in 4/4 (same binary, same node type, same IDF).
- P-b3: control FIRES in 4/4; worst columns are office (`office_*`) series; non-office channels move only
  through shared HVAC.
- P-b4 (reported): U vs R lowers office lighting and equipment energy strongly (code lighting/equipment
  schedules have night and weekend floors that NECB-A occupancy does not: expect office equipment -40 to
  -70 %, office lighting -30 to -60 %), with retail and hotel guest-room lights/equipment also changing;
  residential people-gain changes because 2 people per apartment replaces the density.
- P-b5 (reported): U (linux) vs frozen (win32) is small but may be non-zero (different compiler/libm).

### 3.6 Smoke test (before the array)

One 1-CPU job runs N, R and U on Tall/MTL for 2 days (RunPeriod truncated) and prints N vs R (expect
PASS), U vs R (expect FAIL) and N vs U. It also verifies every uploaded file against `mirror_md5.txt`
and compiles all scripts under the cluster python. Job and outcome in the Ledger.

## 4. V3a design - seed replicates (NOT SUBMITTED)

> **TODO (manager, 2026-09-22): input products = the rebuilt Y2022/2030 products from `IMP/P10R_fix.md`,
> not yet available.** P10 found the current Y2022/B_central products are built on the wrong population
> frame; they will be rebuilt as a new sibling arm. `v3_lib.PRODUCTS` still points at the frozen arm's
> files and must be switched (names + md5s) before V3a runs. `v3a_array.sh` and `v3a_aggregate.sh` refuse
> to run until `/speed-scratch/o_iseri/3J_V3/V3A_INPUTS_READY` exists.

- **Seed handle** (from `IMP/P5_sampling.md` "Seed handles", item 1): the residential household draw,
  `seed` in `channels["residential"]` -> `draw_residential_households(pool, n, seed)`
  (`commercial_integration.py:1847-1865`). No upstream rerun, no GPU. It changes which 27 (Tall) / 41
  (SuperTall) households occupy the apartments. It does NOT re-sample the generator, the Census linkage or
  the office/retail/hotel products (those are single realisations; P5 handles 2-4), so V3a measures
  **residential-draw noise only**, and the reported spread is a lower bound on total sampling noise.
- **Design:** scenarios {Y2022, B_central} x 4 building-city cells x seeds {42, 101, 202, 303, 404} = 40 runs,
  1 CPU each (`tasks_v3a.csv`). Seed 42 doubles as the reproduction check of the (rebuilt) arm on Speed.
  About 40 x 45 min = 30 CPU-hours; with 2 free CPUs about 15 h, with 26 free CPUs one wave (~1.5 h).
- **Pre-registered report (never a gate):** for each published metric, per scenario x cell: mean, SD, min,
  max, range and CV across the 5 seeds - channel EUI (both bases the paper uses: CFA from
  `agg_annual_by_channel.csv`; GFA-share if the Step-9 scorer is added), per-channel peak hour (argmax and
  circular) and coincidence factor from `agg_peak.csv`, and the 2030-minus-2022 delta per channel computed
  within the same seed. Reading rule: a published scenario difference is "larger than draw noise" only if
  |delta| > 2 x SD(delta across seeds). Note P5: MTL and CLG share the same draw for a given seed.
- **Pipeline:** `v3a_array.sh` (40 tasks) -> `v3a_aggregate.sh` (afterok; one Step-8E aggregation per seed
  with `--idf-name injected_resized.idf`, then `v3_check.py v3a`). Outputs:
  `/speed-scratch/o_iseri/3J_V3/agg_V3a/seed<k>/` and `agg_V3a/_check/v3a_{eui,delta,peak}_spread.csv`.
- **Before submitting (checklist):** (1) update `v3_lib.PRODUCTS` to the P10R products; (2) rerun
  `v3_precheck_local.py` (seed-42 rebuild must match the rebuilt arm's IDFs, 0/0); (3) upload the product
  CSVs to `repo/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7/` + refreshed code; (4) `touch
  /speed-scratch/o_iseri/3J_V3/V3A_INPUTS_READY`; (5) `squeue -u o_iseri`, set `--array=0-39%<free CPUs>`;
  (6) `sbatch v3a_array.sh`, then `sbatch --dependency=afterok:<id> v3a_aggregate.sh`.

## 5. Checker - `scripts/V3/v3_check.py`

```
py -3 v3_check.py selftest [--frozen DIR] [--out DIR]     # must PASS before any verdict is trusted
py -3 v3_check.py v3b <runs>/V3b [--frozen DIR] [--out DIR]
py -3 v3_check.py v3a <agg_root> [--frozen-agg DIR] [--out DIR]
```

Seen failing, on REAL frozen captures (`data/V3/v3_check_selftest.txt`, 2026-09-22, SELFTEST PASS):
identical capture PASS (0/0); Y2022 vs Default FAIL (annual 0.655, hourly 0.826); office_lights x(1+2e-6)
FAIL, x(1+5e-7) PASS; one-hour spike of 2e-4 x peak FAIL on the hourly test; missing directory DID_NOT_RUN;
verdict logic on synthetic trees made of real captures: all-equal with X = Y2022 -> PASS (exit 0);
N = Y2022 -> FAIL (1); X = Default -> NOT_EVALUABLE control did not fire (2); U2 missing -> NOT_EVALUABLE
did not run (2); U2 = Y2022 -> NOT_EVALUABLE noise floor (2). `v3b_check.sh` re-runs the selftest on Speed
before scoring.

## 6. Speed layout, commands, logs

- Root: `/speed-scratch/o_iseri/3J_V3/` (uploaded 2026-09-22 by `scp -r`, 94 files, 209 MB; md5 list
  `mirror_md5.txt`, checked inside the smoke job). Code: `repo/3J_docs_occ_nTemp/writing/implementation/IMP/scripts/V3/`.
- Runs: `runs/smoke/`, `runs/V3b/<arm>__Default_NECB__<b>__<c>__s0/` (manifest.json, hourly_meters.csv,
  channel_hourly.csv, dhw*.csv, injected_resized.idf, static_vs_R.txt for N/X, run/eplusout.{sql,err}).
- Logs: `logs/smoke_<job>.out`, `logs/v3b_<array>_<task>.out`, `logs/v3bchk_<job>.out`.
- Submit (on the cluster, after `squeue -u o_iseri`):
  - smoke: `sbatch .../scripts/V3/v3_smoke.sh`
  - V3b: `sbatch .../scripts/V3/v3b_array.sh` (array 0-19%2), then
    `sbatch --dependency=afterany:<V3b array id> .../scripts/V3/v3b_check.sh`
- CPU rule applied: 3J CPUs (running + pending-to-run) <= 32 minus live 1J. At submission 1J ran
  6 x 5 = 30 CPUs (`wp11_draw_task` arrays 1342400 %2 and 1342401 %4), so 3J headroom = 2: the V3b array is
  throttled `%2` and never uses more than 2 CPUs at once; the checker job only starts after the array.
  `histnu` untouched.

## 7. Ledger (append-only)

| When (2026-09-22) | Job | What | State | Output |
|---|---|---|---|---|
| upload | - | mirror to `/speed-scratch/o_iseri/3J_V3/` | done | `mirror_md5.txt` 94 files |
| smoke | 1342424 | N, R, U Tall/MTL, 2 days, 1 CPU | RUNNING at write time (upload md5 guard passed) | `logs/smoke_1342424.out`, `runs/smoke/` |
| V3b | 1342426 | array 0-19%2, `--dependency=afterok:1342424` (starts only if the smoke exits 0) | PENDING (Dependency) | `logs/v3b_1342426_<0-19>.out`, `runs/V3b/` |
| V3b check | 1342427 | `v3b_check.sh`, `--dependency=afterany:1342426` (selftest, then score) | PENDING (Dependency) | `logs/v3bchk_1342427.out`, `runs/V3b/_check/` |
| V3a | - | NOT submitted (manager hold: P10R products) | - | - |
| 2026-09-24 | 1342426 | V3b array 0-19 (U,U2,N,R,X x 4 cells), all COMPLETED | 20/20 `ep_return_code: 0`, 0 severe errors each | `runs/V3b/<arm>__Default_NECB__<b>__<c>__s0/` |
| 2026-09-24 | 1342427 | V3b checker (`v3b_check.sh`: selftest then score) | COMPLETED; selftest PASS; overall verdict NOT_EVALUABLE (noise floor), exit 2 | `runs/V3b/_check/{v3b_summary.txt,v3b_scorecard.json,v3b_effects.csv,v3_check_selftest.txt}` |
| 2026-09-24 | - | local pull, `scp -r .../runs/V3b/_check` | done | `writing/implementation/IMP/data/V3/v3b_check/` (4 files) |

## 8. Next (exact, for a cold agent)

1. On the cluster: `squeue -u o_iseri`; then `tail -8 /speed-scratch/o_iseri/3J_V3/logs/smoke_1342424.out`
   (expect three `status=ok`, `SMOKE N vs R: PASS`, `SMOKE U vs R: FAIL`). If the smoke FAILED, the array
   1342426 shows `DependencyNeverSatisfied`: fix, re-upload the changed file(s) + refreshed `mirror_md5.txt`,
   `scancel 1342426 1342427` (3J's own jobs only), re-run the smoke, resubmit both with the same dependencies.
2. If V3b array and checker are in the Ledger as submitted: when the checker job has ended,
   `cat /speed-scratch/o_iseri/3J_V3/runs/V3b/_check/v3b_summary.txt`, then locally:
   `scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/3J_V3/runs/V3b/_check writing/implementation/IMP/data/V3/v3b_check`
   and record the verdict, the noise floor, the control margin, and the U-vs-R effect table
   (`v3b_effects.csv`, comparison `contract_U_vs_R`) here. Feed U-vs-R to P3 (F-V3-1).
3. V3a: only after `IMP/P10R_fix.md` delivers the rebuilt products - follow the checklist in Section 4.

## 9. What I did not verify

- Tall/CLG and SuperTall/MTL were not pre-checked locally (each Speed N/X task checks N vs R statically
  in-task and records it as `static_vs_R` in its manifest).
- That the frozen injector `cf69d508` and D9 `28714c43` are byte-identical in behaviour to the live code
  beyond the IDFs rebuilt above (only object-level equivalence of the outputs was tested).
- Whether the manuscript intends the pre-T9-9 lights/equipment behaviour (F-V3-1); not decided here.

## 10. V3b result (2026-09-24)

Pulled locally: `scp -r o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/3J_V3/runs/V3b/_check`
-> `writing/implementation/IMP/data/V3/v3b_check/` (4 files: `v3b_summary.txt`, `v3b_scorecard.json`,
`v3b_effects.csv`, `v3_check_selftest.txt`). Everything below is re-read from those files, not copied
from any log or chat message. Only `ls`, `cat`, `tail`, `grep` and `scp` were used on the cluster
(one exception logged in Section 10.6).

### 10.1 Verdict per tower (re-read from `data/V3/v3b_check/v3b_scorecard.json` and `v3b_summary.txt`)

| Cell | Cell verdict | gate N-vs-R | noise U2-vs-U | control X-vs-R |
|---|---|---|---|---|
| Tall_MTL | **PASS** | PASS (ann=0, hr=0) | PASS (ann=0, hr=0) | FIRED (ann=0.0805, hr=1.0) |
| Tall_CLG | **PASS** | PASS (ann=0, hr=0) | PASS (ann=0, hr=0) | FIRED (ann=0.0720, hr=1.0) |
| SuperTall_MTL | **NOT_EVALUABLE (noise floor above TOL/10)** | PASS (ann=0, hr=0) | **FAIL** (ann=2.126e-4, hr=0.5376) | FIRED (ann=0.1050, hr=1.0) |
| SuperTall_CLG | **PASS** | PASS (ann=0, hr=0) | PASS (ann=0, hr=0) | FIRED (ann=0.0933, hr=1.0) |

Overall: **NOT_EVALUABLE (noise floor), exit code 2** (`v3b_summary.txt` line 1, `v3b_scorecard.json`
`"overall"`/`"exit_code"`). This matches the director's stated state exactly.

Keeping the three outcomes apart, all 20 tasks: none DID_NOT_RUN (0/20 missing directories), none
RAN_NOT_FIRED (the control fired 4/4), all 20 RAN and completed (`ep_return_code: 0`, 0 severe errors,
each manifest). The one thing that did not "fire" as expected is the noise-floor precondition on
SuperTall_MTL, which is a FAIL, not a missing or vacuous result.

**SuperTall_MTL stays NOT_EVALUABLE.** Its own gate (N vs R) read a perfect 0/0, but the design
(`V3_design_and_runs.md` Section 3.4, "noise above TOL/10 -> NOT_EVALUABLE") does not let a PASS be
trusted when identical repeat runs (U vs U2) do not agree on that cell, so the clean 0/0 gate reading
is not usable as evidence either way for SuperTall_MTL. No band was moved to rescue it.

### 10.2 Why SuperTall_MTL's noise floor fails (new evidence, from the run manifests)

Pulled by single-file `cat`/`grep`/`tail` over ssh (`runs/V3b/U__.../manifest.json`,
`runs/V3b/U2__.../manifest.json`, and each run's `run/eplusout.err`; no loops, no python on the login
node except the one exception in 10.6):

| Cell | U host (job) | U2 host (job) | Same node? | U warnings | U2 warnings | Warning counts match? | noise verdict |
|---|---|---|---|---|---|---|---|
| Tall_MTL | antenna1 (1342436) | speed-22 (1342481) | no | 91,343,134 | 91,343,134 | yes | PASS |
| Tall_CLG | speed-22 (1342487) | speed-22 (1342516) | yes | 106,955,891 | 106,955,891 | yes | PASS |
| SuperTall_CLG | magic-node-03 (1342562) | magic-node-03 (1342426) | yes | 190,567,533 | 190,567,533 | yes | PASS |
| SuperTall_MTL | speed-22 (1342526) | magic-node-05 (1342559) | no | 152,124,709 | 151,830,748 | **no (delta 293,961)** | FAIL |

(Every count from each run's `run/eplusout.err`, line "EnergyPlus Completed Successfully-- <N> Warning;
0 Severe Errors". Both SuperTall_MTL runs report 0 Severe Errors and `ep_return_code: 0`.)

SuperTall_MTL is the only cell where the two identical-input runs do not even agree on how many
warnings EnergyPlus printed, and it is the only cell that fails the noise floor. Running on different
physical nodes is not, by itself, the explanation: Tall_MTL also ran U and U2 on two different nodes
(antenna1, speed-22) and reproduced its warning count and its energy columns exactly. The mismatch is
specific to the SuperTall/Montreal combination. The worst-column noise in both the annual and hourly
comparisons is `Pumps:Electricity` (`v3b_scorecard.json`, `SuperTall_MTL.noise_U2_vs_U`), and the two
runs' `Electricity:Facility` totals differ by about 4.8e8 J out of 2.69e13 J (`U__.../manifest.json`
`fuel_closure.Electricity.facility_total_J` = 26,928,542,573,859.7 vs `U2__.../manifest.json` same field
= 26,928,060,933,878.0). Separately, all four cells print an unusually large number of warnings for one
annual run (9.1e7 to 1.9e8); this is true of every arm, not only SuperTall_MTL, and is noted here as an
observation only; its cause was not investigated (out of scope for the plumbing question).

**What would make SuperTall_MTL evaluable:** (1) repeat U and U2 pinned to the same compute node
(`--nodelist` or `--constraint` in the sbatch script) and see whether the noise floor closes; this
tests the node-dependence hypothesis directly; (2) if the two runs still disagree on the same node, the
SuperTall_MTL plant model (most likely its pump/plant-loop iteration, given the worst column) has
genuine run-to-run nondeterminism that is a property of that building model, not of the injector, and
would need its own investigation before any SuperTall_MTL number from V3b, V3a or V4 can be trusted at
the precision this design asks for.

### 10.3 Control margin (X-vs-R, office weekday schedule rolled +3 h)

FIRED in 4/4 cells, annual relative change 0.072 to 0.105 (7.2% to 10.5%, worst column
`channel_hourly.csv:office_lights`), hourly relative change 1.0 in all 4 (worst column
`channel_hourly.csv:office_people`, i.e. completely different hour-by-hour against the tolerance's own
normalisation) (`v3b_scorecard.json`, `control_X_vs_R` per cell). Against the pre-registered tolerance
(TOL_ANN 1e-6, TOL_HOURLY 1e-4, Section 3.3), the control margin is roughly 72,000x to 105,000x the
annual tolerance and 10,000x the hourly tolerance; the checker is far from marginal here.

### 10.4 U-vs-R effect table (`contract_U_vs_R`, reported, never gated - Section 3.1 row "U vs R")

Read from `data/V3/v3b_check/v3b_effects.csv` (`rel_change_pct` = 100 x (U - R) / |R|, confirmed from
`scripts/V3/v3_check.py:109,152`). Values are consistent across all 4 cells (spread given); positive =
U (occupancy-linked lights/equipment, the frozen contract) higher than R (code-schedule-rewired):

| Column | rel_change_pct range (4 cells) | hourly range (4 cells) |
|---|---|---|
| Electricity:Facility (whole building) | +16.0% to +17.1% | 0.154 to 0.167 |
| InteriorLights:Electricity | +13.0% to +13.1% | 0.242 to 0.245 |
| InteriorEquipment:Electricity | +29.8% to +30.5% | 0.249 to 0.255 |
| office_lights | +22.8% to +23.8% | 0.290 to 0.308 |
| office_equip | +65.56% (all 4 cells) | 0.4444 (all 4 cells) |
| retail_lights | +61.1% to +61.4% | 0.754 to 0.802 |
| retail_equip | +63.47% (all 4 cells) | 0.7778 (all 4 cells) |
| hotel_lights | -0.43% (Tall) to +1.50% (SuperTall) | 0.782 to 0.829 |
| hotel_equip | +44.40% (Tall) / +46.21% (SuperTall) | 0.345 / 0.355 |
| residential_people | +104.66% (Tall) / +104.82% (SuperTall) | 1.047 to 1.048 |
| residential_lights, residential_equip | 0.0% (unchanged, all 4 cells) | 0.0 |

residential_lights/equip are unchanged because the R contract only touches the apartment PEOPLE
carrier (density -> 2-person households), not residential lights/equipment (Section 3.1 arm
definition); residential_people's +104.7-104.8% is that structural carrier swap, not a schedule effect.

**Disagreement with the pre-registered prediction P-b4.** Section 3.5 predicted "U vs R lowers office
lighting and equipment energy strongly... expect office equipment -40 to -70%, office lighting -30 to
-60%" (code schedules assumed to carry night/weekend floors that occupancy does not). The measured
direction is the **opposite sign**: U reads 22.8-23.8% higher for office lighting and 65.56% higher for
office equipment than R, and every other channel's lights/equipment effect is also positive (U above R),
not negative. This is reported as a measured fact only; no explanation was investigated here and no
band or prediction text has been changed; P-b4 was a pre-registered, reported-only prediction, not a
gate, and it does not affect the PASS/FAIL/NOT_EVALUABLE verdicts above. Flagging it for whoever writes
this into F-V3-1 / P3 (Section 2 above), since it is the opposite of what that section's mechanism
argument expects.

### 10.5 Cross-platform gap (`xplatform_U_vs_frozen`, U on Speed/linux vs the frozen win32 capture) and the tolerance for later use

Read from `v3b_scorecard.json` (`xplatform_U_vs_frozen` per cell), reported only, never gated
(Section 3.1: "U vs frozen ... reported"):

| Cell | annual rel. diff | hourly rel. diff | worst annual col | worst hourly col |
|---|---|---|---|---|
| Tall_MTL | 8.45e-4 | 0.712 | retail_sysheat | Pumps:Electricity |
| Tall_CLG | 8.39e-5 | 0.168 | Heating:NaturalGas | HeatRecovery:Electricity |
| SuperTall_MTL | 8.72e-4 | 0.538 | retail_sysheat | Pumps:Electricity |
| SuperTall_CLG | 2.00e-4 | 0.589 | HeatRejection:Electricity | Pumps:Electricity |

**The pre-registered tolerance (Section 3.3): TOL_ANN = 1e-6, TOL_HOURLY = 1e-4, valid only where the
noise floor (U2 vs U) is <= TOL/10 (1e-7 ann / 1e-5 hourly).** Its basis is explicit in that section:
same binary, same platform, floating-point summation order only (~1e-9 to 1e-12), so 1e-6/1e-4 sits 3+
orders above that floor. That basis is same-binary-same-platform; the design's own comparison table
(Section 3.1) already marks the cross-platform row "reported", never gated, and the measured gap above
confirms why: the cross-platform annual gap alone (8.4e-5 to 8.7e-4) is 84x to 870x TOL_ANN, and the
hourly gap (0.17 to 0.71) is 1,680x to 7,100x TOL_HOURLY, two to three orders above a tolerance that
was sized for same-platform floating noise, not for a different OS/compiler/libm. **No band is loosened
here**: the tolerance is not changed, and it was never proposed as a cross-platform pass/fail line.

**Which later comparison this tolerance still serves.** The 56-cell rebuilt (P10R) campaign now runs
entirely LOCALLY (author ruling 2026-09-24, `Prompts/RESUME.md:3,6-20`, read-only), so there is currently
no Speed-vs-local production comparison for that campaign to serve. The same TOL_ANN/TOL_HOURLY band,
with the same noise-floor precondition, still serves the two comparisons this design already names:
(1) V3b's own `xplatform_U_vs_frozen` check, now recorded above (reported, not gated, as designed); and
(2) the seed-42 run inside the still-pending V3a design (Section 4: "Seed 42 doubles as the reproduction
check of the (rebuilt) arm on Speed"), which is also cross-platform if compared against a local/frozen
capture and should get the same "reported, not gated" treatment this section applied, given the measured
gap above. No new comparison is invented here; nothing else currently on this project's list needs a
Speed-vs-local band.

### 10.6 What I did not verify (this addition)

- The cause of the SuperTall_MTL run-to-run noise (node-pinning was not tested; no repeat run was
  submitted). Section 10.2's "what would make it evaluable" is a proposal, not a result.
- Why every V3b cell prints 9.1e7-1.9e8 EnergyPlus warnings for one annual run; noted, not investigated.
- Why the U-vs-R effect direction is opposite to the pre-registered P-b4 prediction (Section 10.4);
  reported as a measured fact only.
- V3c (`IMP/V3c_fair_control.md`) was not read or touched; it is a separate track being handled
  elsewhere per the execution doc's Progress Log.
- Whether V3a will in fact run on Speed once P10R products land (Section 4 says Speed; not re-confirmed
  here since V3a was not in scope for this task).
- **Process note:** while comparing execution hosts (Section 10.2) I ran one `python3 -c` one-line JSON
  read over ssh on the cluster to print two `manifest.json` fields (`host`, `slurm_job`) for 8 files. This
  is a single-file read equivalent to `grep`, not a loop, not EnergyPlus/compute, and used no cluster
  resources beyond an instant read, but the task's rule for this session was "only single-file
  `cat`/`tail`/`head`/`ls`/`grep`" and the project's standing rule bars python on the login node without
  exception. Flagging it rather than omitting it; a plain `grep -o` would have done the same job and
  should be used if this is repeated.

## 11. V3a results (local, P10R arm, 2026-09-25) - INTERRUPTED, 25 of 40 runs, PARTIAL

Status: **STOPPED by the RAM guard at 03:26:32 UTC with 25/40 runs ok. Not resumed (manager decides).**
Everything below the precheck is PARTIAL and says so. Author ruling: V3a runs locally (Speed full), so
Sections 4 and 6 (Speed layout, `v3a_array.sh`, `v3a_aggregate.sh`) are not used for this run.

### 11.1 What was changed (backups next to each file: `<name>.pre_P10R_2026-09-25.bak`)

- `scripts/V3/v3_lib.py` (md5 now `155818935aef...`): `PRODUCTS` switched to the P10R products in
  `Leg3_4-split/Step7_docs/outputs_step7_P10R/` (Y2022: office `d94d8655...` band observed, retail
  `33708341...`, hotel `7b62a885...`, residential `bdb9b506...`; B_central: office
  `office_presence_multiplier_2030.csv` `d78650c0...` band hybrid, retail `0ec541ae...`, hotel
  `4b3d3a46...`, residential `65a078b7...`). Each md5 equals the P10R cell manifests'
  `INPUTS_HASH_DETAIL` (all 4 cells per scenario), `P10R_products_registry.json`, and the file on disk
  (checked 2026-09-25). Frozen table kept as `PRODUCTS_FROZEN`. New `P10R_CAMPAIGN`, `P10R_STANDBY_FLOOR =
  True`, `p10r_idf()`; `build_injected(..., standby_floor=False)` so V3b N/X keep the frozen wiring.
- `scripts/V3/v3_task.py` (md5 `c1b952a0...`): arm S builds with `standby_floor=True` (the flag
  `3rdJ_08D_campaign_cell_P10R.py` runs with: `preserve_load_standby_floor=True, lighting_model=None,
  dhw_model=None`) and compares statically with the P10R cell (`static_vs_P10R.txt`, manifest
  `static_vs_P10R`, `P10R_PATCH`). The rest of the chain (inject, ensure outputs, D9, D10 resize
  K=1.0 "Laundry Service Water Use 30.6gpm 180F=8.5", one E+ run) was already the P10R chain.
- Every patch prints a `[patch P10R] ...` line (products dir, md5 ok per channel, standby flag, reference
  path); present in every task log (`campaign_local_P10R_V3a/_logs/task_*_attempt1.log`).
- New scripts in `scripts/V3/`: `v3a_precheck_P10R.py` (static check), `v3a_local_driver.py` (10-at-once
  pool, UTC log, one retry, RAM and E+ sampler every 60 s), `v3a_local_aggregate.py` (Windows version of
  `v3a_aggregate.sh`, directory junctions, `--allow-partial`, `--slim`), `v3a_report_P10R.py` (seed-42
  reproduction, spread, 2 x SD reading rule).
- Not done: `hotel_dT_by_type.csv` (the P10R runner writes it; the Step-8E aggregator does not read it,
  so V3a cells do not carry it).

### 11.2 Static pre-check (no simulation), all 4 cells - PASS

`data/V3/v3a_P10R/precheck/precheck_P10R_<b>_<c>.json` (+ `.log`). Live code md5 = P10R
`P10R_CODE_MD5` for all 6 shared files.

| Cell | Y2022 s42 vs P10R | B_central s42 vs P10R | control: Y2022 s101 vs P10R s42 | control: s42 floor OFF vs P10R |
|---|---|---|---|---|
| Tall_MTL | 0/0 | 0/0 | 27/27 PEOPLE (FIRED) | 25/25 LIGHTS + ELECTRICEQUIPMENT (FIRED) |
| Tall_CLG | 0/0 | 0/0 | 27/27 PEOPLE (FIRED) | 25/25 (FIRED) |
| SuperTall_MTL | 0/0 | 0/0 | 41/41 PEOPLE (FIRED) | 25/25 (FIRED) |
| SuperTall_CLG | 0/0 | 0/0 | 41/41 PEOPLE (FIRED) | 25/25 (FIRED) |

The two controls show the check can fail, and fail in the right place: another draw moves exactly one
PEOPLE object per apartment (27 Tall, 41 SuperTall); the frozen wiring moves exactly the 25 objects the
P10R provenance lists as `n_floor_applied=25`.

### 11.3 Run ledger (local, runs root `Leg3_4-split/Step8_docs/campaign_local_P10R_V3a/`)

- Driver: `py -3 -u scripts/V3/v3a_local_driver.py <runs root> --max-par 10`, started 02:16:31 UTC; guard
  `p10r_mem_watchdog.ps1 -Threshold 80 -IntervalS 15 -Log <runs root>/_logs/watchdog.log` started
  02:16:41 UTC. Free disk at start 585 GB; RAM 63.5 GB total, 43.8% used; 20 logical CPUs.
- **Finished ok (25)**, each `ep_return_code 0`, 8760 rows, closures closed: tasks 0-4 (Y2022 Tall MTL, all
  5 seeds), 5 (Y2022 Tall CLG s42), 10-14 (Y2022 SuperTall MTL, 5 seeds), 15-19 (Y2022 SuperTall CLG,
  5 seeds), 30-34 (B_central SuperTall MTL, 5 seeds), 35-38 (B_central SuperTall CLG s42, s101, s202, s303).
  Wall time per task with 10 running: Tall 712-1019 s, SuperTall MTL 1377-1448 s, SuperTall CLG 1512-1870 s.
- **Killed mid-run by the guard (10)**, manifest `status=running`, no valid output: tasks 6-9 (Y2022 Tall
  CLG s101, s202, s303, s404), 20-24 (B_central Tall MTL, all 5 seeds), 39 (B_central SuperTall CLG s404).
- **Never started (5):** tasks 25-29 (B_central Tall CLG, all 5 seeds).
- No task failed on its own (no rc != 0 before the guard). Driver log `_logs/driver.log`; per-task logs
  `_logs/task_NN_attempt1.log`.
- **Guard: ran and FIRED.** `_logs/watchdog.log`:
  `2026-09-25T03:24:55Z [watchdog] used=80.3% p10r_procs=49 energyplus=10`, then
  `2026-09-25T03:26:31Z [watchdog] FIRED used=84.2% >= 80% on 2 samples; p10r_procs=49`, then 49 `KILLED`
  lines at 03:26:31-32Z: 10 energyplus.exe, 11 py.exe + 11 python.exe (driver and tasks), and this
  session's own waiter shells whose command lines contained the runs-root path (15 bash.exe,
  1 powershell.exe, 1 tail.exe). Guard exit 2.
- **Cause: not V3a.** Another session's job on this box, `C:\Users\o_iseri\Desktop\OpenUBEM\...`
  `fleet06c_harvest_2026-09-24.py --cells baseline` (python multiprocessing, 12 workers, about 11 GB),
  started 03:21:46 UTC. With every V3a process gone, RAM was still 74.9% at 03:27 UTC; its largest worker
  alone held 7 GB. That job was not touched.
- RAM trace from the driver sampler (every 60 s): 58-64% with 10 V3a EnergyPlus from 02:17 to 03:12;
  73.2% at 03:14 (before the other job started, reason not identified); 77.6% at 03:23; 82.9% at 03:26:17.
- The same sampler counted 12-13 energyplus.exe box-wide at 03:13 and 03:15. The V3a pool holds at most
  10 tasks (one E+ each, plus a short `energyplus --version` probe per task just before its run); which
  processes made the extra 2-3 is NOT known. A census splitting V3a from other EnergyPlus ran from
  03:21 UTC (`_logs/ep_census.log`): v3a <= 10 and other = 0 in every sample until the guard killed it.

**Resume command (manager decides when; only the 15 unfinished tasks; ok tasks would be skipped anyway):**

```
py -3 -u "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\implementation\IMP\scripts\V3\v3a_local_driver.py" "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step8_docs\campaign_local_P10R_V3a" --max-par 10 --ids 6,7,8,9,20,21,22,23,24,25,26,27,28,29,39
```

then, once the first runs are live (the guard exits 0 after 3 idle samples):

```
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\writing\implementation\IMP\scripts\p10r_mem_watchdog.ps1" -Threshold 80 -IntervalS 15 -Log "C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\3J_docs_occ_nTemp\Leg3_4-split\Step8_docs\campaign_local_P10R_V3a\_logs\watchdog.log"
```

Check RAM first: 10 V3a runs added about 15 points (44% -> 59-64% measured), so start only if RAM used is
below about 60% (below about 65% with `--max-par 5`). Killed tasks rerun from scratch (their manifest is
not `ok`). The guard kills every process whose command line contains `campaign_local_P10R`, including any
waiter or monitor shell that names the runs root. After all 40 are ok, in `scripts/V3/`:
1. `py -3 v3a_local_aggregate.py <runs root> <Step8_docs>\outputs_step8\agg_V3a_P10R` (full mode refuses
   fewer than 8 ok cells per seed);
2. `py -3 v3_check.py v3a <agg_V3a_P10R> --frozen-agg <Step8_docs>\outputs_step8\agg_P10R --out <agg_V3a_P10R>\_check`;
3. `py -3 v3a_report_P10R.py <runs root> <agg_V3a_P10R> <Step8_docs>\outputs_step8\agg_P10R ..\..\data\V3\v3a_P10R\full`;
4. only then shrink the SQLs: rerun step 1 with `--slim` appended (re-aggregates, then slims). The
   aggregator reads only Zones and the calendar from the SQL (`p10r_slim_sql.py` docstring; agg_P10R was
   built from slimmed SQLs). Nothing has been slimmed or deleted yet (full SQLs, about 155-250 MB each).

### 11.4 PARTIAL results (from the 25 finished runs only)

Aggregated per seed over the cells that finished (`v3a_local_aggregate.py --allow-partial`, exit 0 for all
5 seeds; seed 42: 6 cells, 101/202/303: 5, 404: 4) into
`Leg3_4-split/Step8_docs/outputs_step8/agg_V3a_P10R_PARTIAL_2026-09-25/seed<k>/`. Checker
`v3_check.py selftest` PASS (`data/V3/v3a_P10R/selftest_2026-09-25.log`); `v3_check.py v3a` exit 0 into
`agg_V3a_P10R_PARTIAL_2026-09-25/_check/`; report `v3a_report_P10R.py` into
`data/V3/v3a_P10R/partial_2026-09-25/` (`v3a_P10R_report.txt`, `seed42_repro.json`, 4 csv files).

**Seed-42 reproduction of the published P10R cells: exact in 6 of 8 cells.** Hourly captures (15 meters +
36 channel series, V3b checker `compare`): worst annual 0.0 and worst hourly 0.0 in Y2022 Tall MTL, Y2022
Tall CLG, Y2022 SuperTall MTL, Y2022 SuperTall CLG, B_central SuperTall MTL, B_central SuperTall CLG.
Aggregate vs `agg_P10R` for those 6 cells: max abs difference 0 over every numeric column of `agg_annual`
(438 rows), `agg_annual_by_channel` (42), `agg_peak` (222), `agg_diurnal` (13,824), `agg_meta` (6);
0 unmatched rows. B_central Tall MTL and Tall CLG seed 42: DID_NOT_RUN. The comparison was seen failing
first: a copy of agg_P10R with one office EUI x 1.001 read 0.1% (and missing rows read inf).

Spread across seeds, groups with n >= 4 (the rest have n <= 1, no spread):

| Scenario, cell | n | EUI CV across seeds (CFA) | coincidence factor SD |
|---|---|---|---|
| Y2022 Tall MTL | 5 | residential 0.49%, residential_common 0.19%, office 0.10%, others <= 0.08% | 1.5e-4 |
| Y2022 SuperTall MTL | 5 | residential 0.16%, residential_common 0.13%, others <= 0.03% | 2.2e-5 |
| Y2022 SuperTall CLG | 5 | residential 0.11%, residential_common 0.07%, others <= 0.02% | 7.7e-4 |
| B_central SuperTall MTL | 5 | residential 0.28%, residential_common 0.08%, others <= 0.05% | 2.1e-5 |
| B_central SuperTall CLG | 4 | residential 0.24%, residential_common 0.07%, others <= 0.05% | 4.2e-4 |

Peak hour (energy, all days): the argmax hour is identical across seeds in every channel of every group
above, except Y2022 SuperTall CLG office (7, 12, 7, 12, 7: two near-equal peaks, the draw decides which
wins); circular peak-hour SD <= 0.06 h everywhere (largest in residential_common).

**2030-minus-2022, within seed, rule |published delta| > 2 x SD(delta across seeds); published = P10R
(seed 42).** Only SuperTall MTL (5 pairs) and SuperTall CLG (4 pairs) can be read; Tall MTL and Tall CLG
have 0 pairs (B_central Tall not finished).

| Channel | SuperTall MTL published delta (kWh/m2), SD | larger than draw noise? | SuperTall CLG published delta, SD | larger than draw noise? |
|---|---|---|---|---|
| office | -0.450, 0.034 | yes | -0.651, 0.027 | yes |
| retail | -0.725, 0.026 | yes | -4.564, 0.018 | yes |
| hotel | +0.278, 0.026 | yes | +1.032, 0.019 | yes |
| residential | +0.514, 0.343 | **no** (sign changes across seeds) | +0.346, 0.274 | **no** (sign changes) |
| residential_common | +0.049, 0.085 | **no** | +0.182, 0.042 | yes |
| service_MEP | +0.218, 0.013 | yes | +0.317, 0.013 | yes |

Peak-hour and coincidence-factor deltas (same rule, `v3a_P10R_delta_peak.csv`): the circular peak-hour
shift is larger than draw noise for office, retail, hotel, service_MEP and the whole building in both
SuperTall cells, and for residential_common in CLG; not for residential in either city, nor for
residential_common in MTL. The building coincidence-factor change (MTL -0.0009, CLG +0.004) is larger than
draw noise in both. For argmax hours the SD is 0 in most channels, so any non-zero shift (retail -3 h in
MTL and -1 h in CLG, service_MEP +1 h in CLG) counts as larger; the Y2022 SuperTall CLG office argmax flips
with the draw, so office argmax deltas there are not usable.

**Plain reading (partial):** in the SuperTall tower, the published 2030-vs-2022 changes in office,
retail, hotel and service/MEP energy are real signals, 10 to 250 times the draw noise. The residential
change is not: its size (+0.35 to +0.51 kWh/m2) is inside the spread the household draw alone produces,
and its sign flips between seeds. Tall-tower deltas are not yet measured.

### 11.5 What I did not verify

- The Tall-tower 2030-vs-2022 noise (0 seed pairs) and the B_central Tall seed-42 reproduction (not run).
- What pushed RAM to 73.2% at 03:14 UTC, and which processes made the 12-13 EnergyPlus count at
  03:13 and 03:15 (before the census started).
- GFA-share EUI basis (Section 4 lists it "if the Step-9 scorer is added"); only CFA is reported.

## 11.6 FULL results (40 of 40, 2026-09-25)

**All 40 of 40 tasks confirmed ok, not just from the driver log.** The resume run's driver log ends
`2026-09-25T04:30:56.828017+00:00 [driver] done ok=15 failed=0 retried=[] failed_ids=[]`. Checked
independently from the task outputs: `campaign_local_P10R_V3a/V3a/` holds 40 run directories
(`S__<scenario>__<building>__<city>__s<seed>`), and every one of the 40 `manifest.json` files reads
`"status": "ok"`, `"ep_return_code": 0`. With the 25 that finished before the RAM-guard stop, all 40 are ok.

**Aggregation, full mode (no `--allow-partial`):**
`py -3 v3a_local_aggregate.py campaign_local_P10R_V3a outputs_step8/agg_V3a_P10R_2026-09-25` exit 0.
Every seed shows `8 status=ok` cells (the refusal for fewer than 8 never triggered) and every one of the
5 x 8 = 40 cells wrote with `attribution residual 0.000000 %`. The PARTIAL folder
(`agg_V3a_P10R_PARTIAL_2026-09-25/`) was left untouched; the new full result is a separate folder.
`v3_check.py selftest` PASS (`agg_V3a_P10R_2026-09-25/_check_selftest/`).
`v3_check.py v3a agg_V3a_P10R_2026-09-25 --frozen-agg agg_P10R --out agg_V3a_P10R_2026-09-25/_check`
exit 0.

**Seed-42 reproduction, all 8 cells (6 were checked in the partial; B_central Tall MTL and Tall CLG
added here).** `v3a_report_P10R.py` full run, `IMP/data/V3/v3a_P10R/full_2026-09-25/`: all 8 cells PASS,
**worst annual difference 0.0, worst hourly difference 0.0** in every one, the same exact match already
seen in the 6 partial cells. Aggregate vs `agg_P10R` (restricted to the 8 P10R cells): 0 unmatched rows,
max abs difference 0 and max relative difference 0 over every numeric column of `agg_annual` (584 rows),
`agg_annual_by_channel` (56), `agg_peak` (296), `agg_diurnal` (18,432), `agg_meta` (8).

**Spread table, all 8 groups (scenario x building x city), n = 5 seeds in every group now (Tall groups
were n <= 4 or unmeasured in the partial):**

| Group | EUI CV by channel (CFA), highest first | Building coincidence-factor SD | Peak-hour SD (circular, h) |
|---|---|---|---|
| Y2022 Tall MTL | residential 0.49%, residential_common 0.19%, office 0.10%, retail 0.08%, service_MEP 0.08%, hotel 0.03% | 0.000149 | 0.0014 |
| Y2022 Tall CLG | residential_common 0.39%, residential 0.35%, office 0.11%, service_MEP 0.09%, retail 0.05%, hotel 0.02% | 0.001563 | 0.0020 |
| Y2022 SuperTall MTL | residential 0.16%, residential_common 0.13%, office 0.03%, retail 0.02%, hotel 0.01%, service_MEP 0.01% | 0.000022 | 0.0018 |
| Y2022 SuperTall CLG | residential 0.11%, residential_common 0.07%, office 0.02%, retail 0.01%, service_MEP 0.01%, hotel 0.01% | 0.000774 | 0.0018 |
| B_central Tall MTL | residential 0.54%, residential_common 0.21%, office 0.10%, service_MEP 0.08%, retail 0.08%, hotel 0.02% | 0.000167 | 0.0019 |
| B_central Tall CLG | residential 0.47%, residential_common 0.26%, office 0.10%, service_MEP 0.09%, retail 0.07%, hotel 0.02% | 0.001711 | 0.0023 |
| B_central SuperTall MTL | residential 0.28%, residential_common 0.08%, office 0.05%, retail 0.04%, service_MEP 0.03%, hotel 0.02% | 0.000021 | 0.0009 |
| B_central SuperTall CLG | residential 0.21%, residential_common 0.07%, office 0.04%, retail 0.03%, service_MEP 0.03%, hotel 0.02% | 0.000466 | 0.0008 |

The "Peak-hour SD" column above is the whole-building circular peak-hour SD (`_BUILDING`, all days,
energy_W). Per-channel peak-hour SD goes up to 0.117 h (Y2022 Tall CLG `residential_common`) and
0.083 h (B_central Tall CLG `residential_common`); every other channel in every group is at or below
0.03 h. **Largest EUI CV over every channel and every group: 0.543% (B_central Tall MTL, residential).**
**Largest peak-hour SD over every channel and every group: 0.117 h (Y2022 Tall CLG,
residential_common).**

**2030-minus-2022 EUI delta, within seed, all four tower-city cells, all six channels. Rule
(pre-registered): a published delta counts as larger than draw noise only if
|published delta| > 2 x SD(delta across the 5 seeds); published = the P10R arm (seed 42).**

| Cell | Channel | Published delta (kWh/m2, CFA) | SD across seeds | Larger than draw noise? |
|---|---|---|---|---|
| SuperTall CLG | office | -0.651 | 0.024 | yes |
| SuperTall CLG | retail | -4.564 | 0.016 | yes |
| SuperTall CLG | hotel | +1.032 | 0.018 | yes |
| SuperTall CLG | residential | +0.346 | 0.248 | no |
| SuperTall CLG | residential_common | +0.182 | 0.045 | yes |
| SuperTall CLG | service_MEP | +0.317 | 0.011 | yes |
| SuperTall MTL | office | -0.450 | 0.034 | yes |
| SuperTall MTL | retail | -0.725 | 0.026 | yes |
| SuperTall MTL | hotel | +0.278 | 0.026 | yes |
| SuperTall MTL | residential | +0.513 | 0.343 | no |
| SuperTall MTL | residential_common | +0.049 | 0.085 | no |
| SuperTall MTL | service_MEP | +0.218 | 0.013 | yes |
| Tall CLG | office | -0.729 | 0.028 | yes |
| Tall CLG | retail | -4.611 | 0.024 | yes |
| Tall CLG | hotel | +1.053 | 0.019 | yes |
| Tall CLG | residential | +0.236 | 0.190 | no |
| Tall CLG | residential_common | -0.084 | 0.084 | no |
| Tall CLG | service_MEP | +0.342 | 0.015 | yes |
| Tall MTL | office | -0.571 | 0.039 | yes |
| Tall MTL | retail | -0.806 | 0.038 | yes |
| Tall MTL | hotel | +0.327 | 0.046 | yes |
| Tall MTL | residential | +0.438 | 0.253 | no |
| Tall MTL | residential_common | +0.002 | 0.040 | no |
| Tall MTL | service_MEP | +0.172 | 0.031 | yes |

Office, retail and hotel are larger than draw noise in all four cells (12 of 12), by a factor of
**7.1 to 282 times the noise SD** (smallest: Tall MTL hotel, 7.1x; largest: SuperTall CLG retail, 282x).
Service_MEP is also larger than noise in all four cells (5.5x to 28x, not tabulated in the summary
above). Residential is **not** larger than draw noise in any of the four cells (ratio 1.2x to 1.7x,
below the 2x threshold), and its sign flips across seeds in all four (`sign_same_all_seeds = False`
everywhere). Residential_common is larger than noise only in SuperTall CLG (yes); the other three cells
are no.

**Plain reading.** With all 40 runs in, the same pattern holds in the Tall tower that the partial result
already showed in the SuperTall tower: the published 2022-to-2030 change in office, retail, hotel and
service/MEP energy is a real signal, far bigger (7 to about 280 times) than the spread five different
household draws alone produce. The household (residential) change is not a real signal in any of the
four city-tower combinations: its size sits inside the noise band, and it does not even keep the same
sign from one draw to the next. The five-seed spread itself is small everywhere: no channel in any
group moves more than about half a percent from seed to seed, and the peak usage hour barely moves
(at most about a tenth of an hour, in the household-common-area channel of the Montreal and Calgary
Tall towers).

### 11.7 What I did not verify (full run)

- The `--slim` SQL-shrink step (section 11.3 step 4) was **not run**. It is described in section 11 as
  safe (the aggregator only reads Zones and the calendar from each SQL, and `agg_P10R` itself was built
  from slimmed SQLs), but the task that produced this section did not ask for it, so the 40 run folders
  still hold their full `eplusout.sql` files (about 155-250 MB each) exactly as the runs left them.
  Skipped, not attempted.
- What pushed RAM to 73.2% at 03:14 UTC during the first (interrupted) run, and which processes made the
  12-13 EnergyPlus count at 03:13 and 03:15 (carried over from section 11.5; irrelevant to the full
  result since all 40 tasks now show `ep_return_code 0`).
- GFA-share EUI basis: not computed here either; only CFA is reported (same limitation as section 11.5).
- Whether the residential 2030-vs-2022 change would clear the noise bar with more than 5 seeds; only
  5 seeds were drawn, per the pre-registered design.
- The full-mode and `--slim` paths of `v3a_local_aggregate.py` have not run yet (partial mode only).

## 11.8 FULL results after the hotel observed levels (2026-09-25)

The 2030 hotel recovery levels were switched to the observed 2023-2025 means (AB 0.597, QC 0.610), so the
20 B_central repeat-seed runs (task ids 20-39) were re-run on this computer with the new hotel CSV
(md5 300716728df0c314e129fc544f386c70). The 20 Y2022 runs do not read that file and were kept.

- Runs: driver `done ok=20 failed=0` (18:37:20Z); all 40 manifests OK. Control: the new md5 appears in
  20 of 20 B_central manifests and 0 of 20 Y2022 manifests. RAM peaked at 69.7% (guard at 88% never fired).
- Aggregate: `outputs_step8/agg_V3a_P10R_hotel_obs`, every seed 8/8 cells ok, attribution residual 0 on
  all 40 (log `campaign_local_P10R_V3a/_logs/aggregate_hotel_obs.txt`). `v3_check.py v3a` exit 0 (tables in
  `_check/`). Report: `IMP/data/V3/v3a_P10R/full_hotel_obs/`.
- Positive control: seed 42 reproduces the re-run `agg_P10R` exactly in all 8 cells (worst annual and
  hourly difference 0.0; every aggregate table 0 unmatched rows, max_abs 0).

Compared with section 11.6:

- Largest EUI CV: 0.542% (B_central Tall MTL residential), unchanged; about 0.5% still holds.
- Largest peak-hour SD: 0.117 h (Y2022 Tall CLG residential_common), unchanged; about 0.1 h still holds.
- Office, retail and hotel 2030-minus-2022 changes are now 5.4 to 311 times the draw SD (smallest Tall MTL
  hotel, largest SuperTall CLG retail), was 7.1 to 282. Office 14.7-29.6, retail 22.7-311, hotel 5.4-37.6.
  Sign the same in all 5 seeds for all three. service_MEP 4.3-60.7.
- Residential: 1.15-1.60 times, sign flips in all 4 cells (unchanged verdict). residential_common above
  noise only in SuperTall CLG (3.0), unchanged.
- New published hotel deltas (kWh/m2 CFA): SuperTall CLG +0.629, SuperTall MTL -0.226, Tall CLG +0.628,
  Tall MTL -0.255 (was +1.032, +0.278, +1.053, +0.327). The Montreal hotel change is now a small decrease.
- Manuscript: `05_Limitations.md` line 3 "7 to 280 times" -> "5 to 310 times" (only change, CRLF kept,
  backup in `chapters_v2/_archive_pre_hotel_obs_2026-09-25/05_Limitations.md`). The 0.5 %, 0.1 h and
  residential sentences stand.

### 11.9 What I did not verify (hotel observed re-run)

- `--slim` was again not run; the 20 new run folders keep their full SQL files.
- (Checked, not open) No manuscript sentence states the sign of the 2030-minus-2022 hotel change: grep of
  Results, Discussion, Conclusion, Introduction and front matter for hotel + rise/increase/decrease finds only
  Results line 58 (injected vs code, a different comparison) and the section 3.3 lever effects (vs central 2030).
- GFA-share basis: not computed (CFA only), as in 11.5 and 11.7.
