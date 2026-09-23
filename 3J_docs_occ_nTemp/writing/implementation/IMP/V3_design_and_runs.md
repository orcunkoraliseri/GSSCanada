# V3 - plumbing check (V3b) and seed replicates (V3a): design and runs

Task doc:  `writing/implementation/3J_IMP_execution_2026-09-22.md` section "V3"; plan Section 7a.
Status:    V3b IN PROGRESS - smoke 1342424 running; V3b array 1342426 (afterok smoke) and checker 1342427
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
