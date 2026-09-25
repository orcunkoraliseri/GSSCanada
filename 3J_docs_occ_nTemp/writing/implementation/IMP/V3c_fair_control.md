# V3c -- fairer code-schedule control (dwelling-unit occupancy for apartments and guest rooms)

Task doc: `writing/implementation/3J_IMP_execution_2026-09-22.md` section "V3c"; manager finding M-1
(2026-09-22, P3 entry) and the V3c-ADDED progress-log entry (2026-09-22). Written BEFORE submitting,
per instruction. Reuses the V3 Speed setup exactly (`IMP/V3_design_and_runs.md`), never touches V3b's
jobs 1342424/1342426/1342427.

## 1. Why

Manager finding M-1: the uninjected code-schedule control (`Default_NECB`) puts apartments and hotel
guest rooms on `NECB-A-Occupancy`, the NECB **office** occupancy schedule, not a residential one. P3's
presence-reversal result (hotel/residential shift to night in the survey-driven arms) is therefore
partly a property of an unfair control. V3c builds arm **F**: identical to the frozen uninjected IDF
except those PEOPLE objects reference the NECB **dwelling-unit** occupancy schedule instead. Its
result decides one sentence: whether the hotel/residential night-presence contrast survives against a
residential-shaped code schedule.

## 2. Base and scope

Base = the 4 uninjected `Default_NECB` cells (Tall/SuperTall x MTL/CLG), byte-identical to V3b's arm
U: `Leg3_4-split/Step8_docs/campaign_local_deliverable/Default_NECB__<Tall|SuperTall>__<MTL|CLG>/
injected_resized.idf`. (V3's `U` variant on Speed is this same IDF, per `IMP/V3_design_and_runs.md`
section 3.1.)

## 3. Evidence for the NECB dwelling-unit schedule (not invented)

- NECB assigns schedule letter **G** to residential space types: `improvements/v2/
  f8_necb_schedule_evidence/space_types_NECB2011.json`, table `space_types`, rows with
  `necb_schedule_type=="G"` include `building_type=="Multi-unit residential"`
  (`occupancy_schedule=="NECB-G-Occupancy"`) and `space_type=="Dwelling Unit(s)"` (same). 15 rows
  total carry `necb_schedule_type=="G"`; these two are the residential ones (others are
  schedule-G corridors/mechanical rooms that ride the dwelling-unit schedule by NECB rule, not
  residential themselves).
- Values: `improvements/v2/f8_necb_schedule_evidence/sched_NECB2011.json`, table `schedules`, the 3
  rows with `name=="NECB-G-Occupancy"` (`day_types` = `Default|Wkdy`, `Sat`, `Sun|Hol`, all
  `type=="Hourly"`, 24 values each). **Identical** in `sched_NECB2015.json` (checked, both files).
  Values (fraction of the density peak), hour 1 = 00:00-01:00 ... hour 24 = 23:00-24:00:
  - Weekday: `0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.7 0.4 0.3 0.3 0.3 0.3 0.3 0.3 0.3 0.3 0.5 0.9 0.9 0.9 0.9 0.9 0.9`
  - Saturday: `0.9 0.9 0.9 0.9 0.9 0.9 0.9 0.7 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.7 0.9 0.9 0.9 0.9 0.9 0.9`
  - Sunday|Holiday: identical to Saturday (checked equal, both source files).
  This is a residential pattern -- high overnight, a midday dip (occupants at work/school), rising in
  the evening -- the opposite shape of `NECB-A-Occupancy` (0 overnight, a daytime office bump, 0
  weekends).
- Day-type mapping for the new `Schedule:Compact` object copies the structure the frozen
  `NECB-A-Occupancy` object already uses (read directly from `campaign_local_deliverable/
  Default_NECB__Tall__MTL/injected_resized.idf:11429-11674`): `Weekdays = WinterDesignDay =
  SummerDesignDay` = the `Default|Wkdy` row; `Saturday` = `Sat` row; `Sunday` = `Sun|Hol` row.
- The 4 PEOPLE objects that reference `NECB-A-Occupancy` for apartments/guest rooms (same line
  offsets in all 4 cells, checked): `HighriseApartment Apartment People` (line 72424 Tall/MTL,
  72424 Tall/CLG, 105872 SuperTall/MTL, 105872 SuperTall/CLG), `LargeHotel GuestRoom5/6/7 People`
  (lines 72532/72550/72568 Tall cells, 105980/105998/106016 SuperTall cells).

No value in this file was invented; every number above traces to a file:line or a JSON row cited next
to it.

## 4. Build (arm F) and negative control -- code and result

Script `writing/implementation/IMP/scripts/V3/v3c_build_F.py`: takes the frozen `Default_NECB`
`injected_resized.idf`, re-points exactly those 4 PEOPLE objects' "Number of People Schedule Name"
field from `NECB-A-Occupancy` to `NECB-G-Occupancy`, and appends ONE new `Schedule:Compact` object
(`NECB-G-Occupancy`, values in section 3) built from the same helper (`v3_build_R.objects`/`fmt`) V3b's
arm R uses, for text-format consistency. Self-check inside `build()`: refuses unless exactly 4 objects
changed and exactly 1 added (raises `SystemExit`, would fail the sbatch task). Lights and equipment of
these Spaces are untouched (still their own PNNL prototype schedules, e.g. `ApartmentHighRise
LTG_APT_SCH`, `HotelLarge BLDG_LIGHT_SCH_2013`) -- unlike arm R, which re-points lights/equipment too.

Negative control, `writing/implementation/IMP/scripts/V3/v3c_static_check.py`: reuses `v3_static.py`
(the same object-level IDF comparator V3b's gate uses -- schedule references are expanded to their
12-month x 12-day-type x 48-half-hour content, so the diff shows only where a PEOPLE object's
*resolved* schedule changed, not the new schedule definition itself). PASS condition: F vs U differs
in exactly 4 objects, all class `PEOPLE`. Control: build F, then ALSO re-point one out-of-contract
object (`HighriseApartment Apartment Lights`) to `NECB-G-Occupancy`, and require the checker to show
more than 4 diffs / a non-`PEOPLE` class.

**Run locally, 2026-09-22** (`py -3 v3c_static_check.py <campaign_local_deliverable> <tmp>`), seen
both ways as required (CLAUDE.md "a check must be seen failing before it is trusted"):
```
REAL CHECK (F vs U, 4 cells): PASS
  Tall/MTL: pass=True only_a=4 only_b=4 classes_a=['PEOPLE']
  Tall/CLG: pass=True only_a=4 only_b=4 classes_a=['PEOPLE']
  SuperTall/MTL: pass=True only_a=4 only_b=4 classes_a=['PEOPLE']
  SuperTall/CLG: pass=True only_a=4 only_b=4 classes_a=['PEOPLE']
NEGATIVE CONTROL (F + stray lights edit, Tall/MTL): FIRED (correctly caught) (only_a=5, classes_a=['LIGHTS', 'PEOPLE'])
OVERALL: PASS
```
So: the real edit touches only what it should (4 cells x 4 PEOPLE objects, nothing else), and a
deliberately broader edit (also touching a LIGHTS object) is caught (5 diffs, an extra class) -- the
control fires. `v3c_build_F.py`'s own self-check additionally confirms `objects_changed==4,
objects_added==1` on all 4 real Speed builds (recorded in each task's `manifest.json`, `build_F` key).

## 5. Runner and submission

Standalone runner `v3c_task.py` (does NOT import or edit `v3_task.py`, so V3b's pending jobs are never
touched): one row of `tasks_v3c.csv` (4 rows, arm F, `Default_NECB` x 4 building-city cells) -> build F
-> `v3_lib.run_eplus` (same Speed EnergyPlus 24.2.0 Singularity image V3b uses, `/speed-scratch/
o_iseri/step9_spike/energyplus_24.2.0.sif`) -> `v3_lib.postprocess` (same campaign writer). Output:
`/speed-scratch/o_iseri/3J_V3/runs/V3c/F__Default_NECB__<b>__<c>/manifest.json,
hourly_meters.csv, channel_hourly.csv, dhw*.csv, injected_resized.idf, run/eplusout.{sql,err}`.
Sbatch `v3c_array.sh`: `-p ps --cpus-per-task=1 --mem=8G -t 7-00:00:00 --array=0-3`, 1 CPU per task, no
throttle (see CPU check below).

Files uploaded (`scp`) to `/speed-scratch/o_iseri/3J_V3/repo/3J_docs_occ_nTemp/writing/implementation/
IMP/scripts/V3/`: `v3c_build_F.py`, `v3c_static_check.py`, `v3c_task.py`, `v3c_array.sh`,
`tasks_v3c.csv`. md5 checked equal to local copies (both listed in the Ledger). `tasks_v3c.csv` also
copied to `/speed-scratch/o_iseri/3J_V3/` (the runner reads `$ROOT/tasks_v3c.csv`, matching where
`tasks_v3b.csv`/`tasks_v3a.csv` already live -- the first submission failed on this exact path
mismatch, see Ledger).

**CPU check** (`squeue -u o_iseri`, both before submissions): live non-`histnu` CPUs = 6 (1J's
`wp11_dra` arrays 1342400/1342401, running at their own throttle limits 2+4). 3J's own live+pending:
smoke 1342424 (1 CPU, running) + V3b array 1342426 (up to 2 CPUs, pending on smoke). Budget
32 - 6 = 26 for 3J; V3c's 4 x 1 CPU fits with room to spare, so no `%` throttle and no
`--dependency` needed. Account-wide cap (`histnu` 32 + shared 32 = 64) is tighter at the moment:
after submission task 0 started running immediately, tasks 1-3 sat `PD (AssocGrpCpuLimit)` -- expected,
resolves itself as any job of any kind finishes; not a 3J-vs-1J issue.

## 6. Post-processing (for the next agent -- not run here)

Once all 4 `runs/V3c/F__*/manifest.json` say `"status": "ok"`, reuse the Step-8E aggregator (the same
CLI V3a's design already calls for, `IMP/V3_design_and_runs.md` section 4) rather than re-deriving
per-channel energy shares by hand:

```
PY=/speed-scratch/o_iseri/envs/step4/bin/python
$PY Leg3_4-split/Step8_docs/3rdJ_08E_aggregate_4split.py \
    --campaign-dir /speed-scratch/o_iseri/3J_V3/runs/V3c \
    --outdir /speed-scratch/o_iseri/3J_V3/agg_V3c_F \
    --eplus-idd $EPLUS_IDD --idf-name injected_resized.idf
```
(cells must sit directly under `--campaign-dir` as `<label>/`, which `v3c_task.py` already does --
`runs/V3c/F__Default_NECB__<b>__<c>/`). Then compare against U's own aggregate: U is already inside
`agg_deliverable` (scenario `Default_NECB`, the published control) -- do NOT re-aggregate it, reuse
`Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/agg_{peak,diurnal,meta,annual_by_channel}.csv`
filtered to `scenario=="Default_NECB"`, exactly as `writing/implementation/IMP/scripts/
p3_code_schedule_comparison.py` already reads it (`load()`, `wd_profile()`, `CH6`/`TENANT`
definitions, `circ()` for the circular-mean peak hour) -- reuse those functions rather than
reimplementing the peak-hour/coincidence-factor/EUI math a second time.

Outputs to compare (F vs U, both 2022 code-schedule arms, no scenario claim beyond that):
- Per-channel weekday presence by hour: `agg_diurnal.csv` filtered `channel in {office, retail,
  hotel, residential}`, `season=="all"`, `daytype=="WD"`, `metric=="people_frac"` if present, else the
  4 channels' `_people` column of `channel_hourly.csv` directly, hour-of-week averaged (weekday flag:
  `RunPeriod` starts Sunday 2006-01-01, 8760 non-leap hours, `pandas.date_range("2006-01-01",
  periods=8760, freq="h")`, `.dayofweek < 5`).
- Peak hour per channel (`circ()` on the weekday profile) and whole-building peak hour
  (`agg_peak.csv`, `channel=="_BUILDING"`, `peak_hour_circular`).
- Coincidence factor: `agg_peak.csv`, `channel=="_BUILDING"`, `coincidence_factor` column (already the
  Step-8E definition P3 controls reproduced: 0.9301 code / 0.9402 Y2022 / 0.9409 B_central, median of
  4 cells -- `3J_IMP_execution_2026-09-22.md` 2026-09-22 P3 manager check).
- Channel EUI: `agg_annual_by_channel.csv` (CFA and GFA-share bases, same two bases P3/P9 already use).
- F vs U: the same table shape P3's `data/P3_comparison_summary.csv` already writes; add a `arm`
  column (`U` / `F`) and diff. One sentence verdict: does F's hotel/residential night-presence pattern
  still contrast with the survey-driven arms once the control itself is residential-shaped, or does the
  contrast shrink/vanish.

## 7. Ledger (append-only)

| When (2026-09-22) | Job | What | State | Output |
|---|---|---|---|---|
| local | - | `v3c_build_F.py` + `v3c_static_check.py` written, compiled (`py -3 -m py_compile`), run locally | PASS (section 4) | this doc section 4 |
| upload | - | scp 5 files to `/speed-scratch/o_iseri/3J_V3/repo/.../scripts/V3/`; md5 checked equal local/remote | done | md5s: `v3c_build_F.py` 1a49f6cf..., `v3c_static_check.py` 9526bc67..., `v3c_task.py` 772097ab..., `v3c_array.sh` 0c27f0b1..., `tasks_v3c.csv` 4ebefcce... |
| submit 1 | 1342430 | `sbatch v3c_array.sh`, array 0-3 | FAILED all 4, 1 s each (`FileNotFoundError: tasks_v3c.csv` -- runner looks for `$ROOT/tasks_v3c.csv`, not `$CODE/tasks_v3c.csv`) | `logs/v3c_1342430_*.out` |
| fix | - | `cp` `tasks_v3c.csv` from `$CODE` to `$ROOT` (`/speed-scratch/o_iseri/3J_V3/tasks_v3c.csv`), md5 checked equal | done | - |
| submit 2 | **1342434** | `sbatch v3c_array.sh`, array 0-3, 1 CPU each, no throttle | task 0 RUNNING (EnergyPlus 24.2.0-94a887817b confirmed in log at submit+~18s); tasks 1-3 PENDING (`AssocGrpCpuLimit`, account-wide, resolves as any job finishes | `logs/v3c_1342434_<0-3>.out`, `runs/V3c/F__Default_NECB__<b>__<c>/` |

## 8. Next (exact, for a cold agent / the manager)

1. `squeue -u o_iseri` then `sacct -j 1342434 --format=JobID,JobName,State,ExitCode,Elapsed -X`; if
   all 4 `COMPLETED` with `ExitCode 0:0`, check each `runs/V3c/F__*/manifest.json` for
   `"status": "ok"` and `"build_F": {"objects_changed": 4, "objects_added": 1, ...}`.
2. Run the Step-8E aggregation command in section 6, then the P3-style comparison reusing
   `p3_code_schedule_comparison.py`'s functions. Write results + the one-sentence verdict to this file
   (append, do not overwrite sections 1-7) or to a sibling `IMP/V3c_results.md`.
3. Per-cell run time budget ~45 min (same platform as V3b, `IMP/V3_design_and_runs.md` section 1); do
   not poll -- check back after that.

## 9. What I did not verify

- Whether `agg_diurnal.csv` carries a `people_frac`-style normalized presence metric or only raw watts
  in the `_people` columns -- local disk on this machine was essentially full while writing this doc
  (`df -h C:` showed 140 MB free of 1.9 TB) and a pandas read of the frozen `agg_*.csv` files failed
  with `OSError: No space left on device` mid-check; **worth flagging to the manager independently of
  V3c** since it could affect any other local write/run. The post-processing command in section 6
  gives both the normalized-metric path and the raw-`_people`-column fallback so the next agent is not
  blocked by this.
- Did not run EnergyPlus locally on win32 for arm F (no cross-platform check for F, unlike V3b's U vs
  frozen); not asked for, and Speed already matches V3b's own platform choice.
- Did not check whether `agg_annual_by_channel.csv`'s EUI is on CFA or requires the Step-9 scorer for
  the GFA-share basis; noted as a fallback path in section 6 rather than assumed.

## 10. Post-processing done, results (2026-09-24, append)

Array 1342434 verified COMPLETED 4/4 (0:0), all 4 manifests `status: ok`,
`build_F: objects_changed=4, objects_added=1`. Cluster was full, so the author ruled (2026-09-24)
to aggregate locally instead of by sbatch: cells copied `scp -r` to
`C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/3J_V3c/runs/V3c/`, Step-8E aggregator run locally
(one process, RAM checked at 49.9% before running), output `IMP/data/V3c/agg_V3c_F/agg_*.csv`,
attribution residual 0.0% on all 4 cells. Comparison script `IMP/scripts/v3c_compare.py` (imports
`p3_code_schedule_comparison.py`'s functions) compares F against U (frozen `agg_deliverable`,
read-only, not re-aggregated). Both required gates run and recorded: U-vs-U shows exactly zero
difference; a deliberately altered copy shows a nonzero difference localized to the altered rows
only. Full numbers, tables, and the one-sentence verdict are in the sibling doc
`writing/implementation/IMP/V3c_results.md` (do not duplicate here -- that file is the source of
record for V3c's result). Headline: F's hotel/residential weekday night presence jumps from
near-zero (U) to a night-peaked pattern as large as, or larger than, the survey-driven arms'
(Y2022/B_central) -- the P3 presence-reversal contrast against the code control shrinks sharply
once the control itself is residential-shaped, confirming it was largely a limitation of the
unfair NECB-A control rather than a property of the survey data.
