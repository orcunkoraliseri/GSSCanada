# Manager prompt — 3J Leg-3 Step 9, morning of 2026-08-01

Paste this whole file as the first message of a fresh session. It is self-contained: it assumes
no memory of the 2026-07-31 session.

---

You are the manager on the 3J Leg-3 four-channel mixed-use tower BEM pipeline. Work in
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`.

## Standing rules — non-negotiable

- 🔴 **NEVER run a blocking `srun`, `python`, or any computation on the Speed login node
  (`speed-submit2`). ALWAYS `sbatch`.** This has been flagged three times; one more is account
  suspension. Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`,
  `cd`, `ls`, `scp`, `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`.
  `tar`, `find` and `python` are **not** allowed there.
- **Every job requests `-t 7-00:00:00` minimum.** No exceptions, even for one-minute probes.
- Cluster commands single-line, each labelled "locally" or "on the cluster".
- **Never widen a band or relax a gate to erase a FAIL.** The remedy is re-specification or an
  explicit `N/A`. A gate counts as validation only once it has been *seen failing*; write the
  falsifiable prediction **before** running the test.
- **Update the Progress Log live** — same response as each state change, not batched at the end.
  The live doc is `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md` (1841 lines).
  Agents never write it; the manager consolidates.
- **Leg-2 is closed and paper-ready — read-only.** No file under `Leg2_2-split/` may be modified.
- All documents in English. The user writes French; reply in English.
- `python` is not on PATH locally — use `py -3`. Speed's remote shell is **tcsh**, so bash
  redirects like `2>/dev/null` fail with "Ambiguous output redirect".
- Cheap models for mechanical work; minimum monitoring frequency 30 min; never poll in a loop.
- Max ~100 words per reply unless detail is asked for.
- Don't trust a number quoted in a log — re-derive it from the artefact's own columns.

## What is running right now

**Campaign array `1170771`** on Speed, 112 tasks, `--array=0-111%20`, submitted 2026-07-31 ~21:4x
after pre-flight job `1170770` printed **VALIDATION PASS**.

| arm | tasks | `--lighting-model` | `--dhw-model` | outroot |
|---|---|---|---|---|
| C | 0–55 | `calibrated_v2` | `none` | `campaign/out_C_lm3v2/campaign_39a6e24e` |
| D | 56–111 | `calibrated_v2` | `per_capita` | `campaign/out_D_full/campaign_39a6e24e` |

Two arms so the changes can be **attributed, not confounded**: `C − B` is the pure T9-12
retail-lighting effect, `D − C` is the pure T9-11 DHW effect.

Cluster root: `/speed-scratch/o_iseri/step8_4split/campaign/`.
Injector md5 `39a6e24e59bfcce09a1ce095af613274` (also `INJ_HASH=39a6e24e`).

## First actions, in order

1. **On the cluster:** `ssh speed "sacct -X -j 1170771 --format=State -n | sort | uniq -c"` —
   expect `112 COMPLETED`. Any FAILED/TIMEOUT is a stop; read the task log in
   `campaign/logs/campCD_1170771_<task>.out`.
2. **On the cluster, aggregate both arms** (scripts are already uploaded and correct):
   `ssh speed "sbatch /speed-scratch/o_iseri/step8_4split/campaign/agg_armC.sh"` and the same for
   `agg_armD.sh`. They write `campaign/agg_C_lm3v2` and `campaign/agg_D_full`.
   ⚠️ The association CPU cap is `cpu=32`; if an aggregation sits in `AssocGrpCpuLimit` while the
   array is still draining, lower the throttle
   (`scontrol update jobid=1170771 arraytaskthrottle=7`) and **restore it to 20 afterwards** —
   the user asked for that explicitly last time.
3. **Locally, download** into the session scratchpad and run the comparison. The arm-B analysis
   script `analyse_armB.py` (three-way pre/A/B) is the template — point it at `aggC`/`aggD`.
   Prior aggregates for the controls: arm A and arm B are on the cluster at `campaign/agg_A_t99`
   and `campaign/agg_B_lm3`; pre-fix is local at
   `Leg3_4-split/Step8_docs/outputs_step8/agg`.
4. **Integrity before any delta** — this is not optional. Same 56 cell tags across arms,
   `attribution_closed=True` everywhere, and `max |area_X − area_Y| = 0 m²`. If the areas differ,
   the arms are not comparable and nothing below means anything.

## The five predictions — written 2026-07-31, BEFORE the runs. Do not edit them.

1. **C vs B: retail EUI FALLS** from 95.39 toward ~88–91, and retail lighting stops being frozen —
   the 13 injected scenarios must show a **non-zero spread** where arm B had 339.0211 GJ in every
   one. *If retail lighting is still identical across scenarios in arm C, T9-12 did not land.*
2. **C vs B: office and hotel UNCHANGED** to within noise. T9-12 touches retail only (proved at
   schedule level by V7). Any office/hotel movement means leakage.
3. **The retail gate does NOT stay 56/56.** Arm B's PASS was bought by the freeze; removing it
   should put retail back near `Default_NECB` (87.6–97.1) and make the gate genuinely uncertain.
   A PASS here would be meaningful where arm B's was not.
4. **D vs C: DHW stops being flat.** Office `dhw` was 12.19 kWh/m² in every scenario column to
   2 dp; in arm D it must differ between B_cons and B_opt. The schedule-level lever was −18.85 %,
   so expect a visible but smaller energy lever.
5. **D vs C: hotel moves LEAST in relative terms** despite DHW being 36.7 % of hotel energy,
   because ~54 % of design DHW flow is the excluded laundry. If hotel DHW moves as much as
   residential, the laundry exclusion did not hold.

## State of the gates — carry these forward honestly

| channel | band | status after arm B | note |
|---|---|---|---|
| office | [100,200] | **FAIL 0/56** | ~15 of the 22 kWh/m² shortfall is the standalone-prototype band, not the occupancy model (`Default_NECB` = 85.29 vs floor 100). Not expected to pass. |
| retail | [80,155] | **FAIL** (arm A's number stands) | arm B's 56/56 PASS is **rejected on mechanism** — bought by freezing retail lighting. |
| hotel | [180,300] | **FAIL 28/56** | bimodal: SuperTall 149–165 vs Tall 195–212, **nothing in [170,182)**. The median crossing 180 is an artefact of a median in an empty gap. |

No band, threshold or gate has been edited. Three FAILs stand.

## Open items, not yet decided by the user

- **Office gate**: recommendation on file is to verify then demote `S9-EUI-office` to INFO and
  promote the exposure-ordering test in `3rdJ_09X_envelope_exposure.py` to PASS/FAIL. Needs the
  user's call.
- **Hotel gate**: recommendation is to split it by geometry. Needs the user's call.
- **Retail NECB proxy** at `3rdJ_07_aug_to_bem_4split.py:20-45` — still provisional. T9-12 reduced
  its weight from 100 % to 60 % but did not resolve it.
- **Hotel laundry**, ~54 % of design DHW flow, still occupancy-invariant by deliberate scope call.
  A correct model scales the batch shape by a daily/monthly occupancy factor against a fixed
  cross-scenario reference; choosing that reference is a specification decision.
- **Leg-2 manuscript office EUI** is inflated ~1.706× by `calculate_eui()` missing a `ReportName`
  filter (`Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py:293-299`). Leg-2 is read-only —
  this is a manuscript caveat to raise, not a file to edit.

## What was done on 2026-07-31 (context, not tasks)

Campaign `1170493` closed 112/112. Arm A (T9-9 standby floor) and arm B (T9-9 + T9-10 lighting
diversity) analysed. Six of seven pre-recorded predictions passed; the load-bearing one — office
lighting WFH lever shrinking −16.2 % → −10.5 % — passed, confirming `office_n=3`. Arm B exposed
that T9-10's retail rule froze retail lighting, which produced **T9-12** (retail re-specified as
`g = open·[k + (1−k)·occ]`, k=0.60 calibrated to the NECB prototype's own weekday mean, 8/8
predictions pass, not yet simulated → that is what arm C answers). **T9-11** (occupancy-driven
DHW, 8/8 predictions pass) had never been simulated either → that is what arm D answers.

Full detail with every number and every falsified prediction:
`3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md`.
Memory: `project_3j_leg3_step9_status.md`.
