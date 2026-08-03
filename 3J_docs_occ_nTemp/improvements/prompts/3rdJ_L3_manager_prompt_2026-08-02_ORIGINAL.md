# Manager prompt — 3J Leg-3 Step 9, morning of 2026-08-02

Paste this whole file as the first message of a fresh session. It is self-contained: it assumes
no memory of the 2026-07-31 or 2026-08-01 sessions.

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
- 🔴 **Vacuous tests are the recurring failure on this project — six kinds so far.** Before
  recording any PASS, ask: *what result would have made this fail?* If nothing could, it is not a
  test. Live examples in the log: a pivot whose spread was 0 by construction, an identity dressed
  as a hypothesis, a gate declared in the doc but never written in code, an explanation that could
  not be wrong, and — on 2026-08-01 — a *specification argument* ("Default_NECB makes the
  uninjected cell an exact no-op") that was true of every candidate and therefore chose none.
- **Update the Progress Log live** — same response as each state change, not batched at the end.
  The live doc is `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md` (**2313 lines**).
  It is the main document of record. Agents never write it; the manager consolidates.
- **Leg-2 is closed and paper-ready — read-only.** No file under `Leg2_2-split/` may be modified.
- All documents in English. The user writes French; reply in English.
- `python` is not on PATH locally — use `py -3`. Speed's remote shell is **tcsh**, so bash
  redirects like `2>/dev/null` fail with "Ambiguous output redirect". But `sbatch --wrap` runs
  under **bash** — use `export`, not `setenv`.
- Cheap models for mechanical work; minimum monitoring frequency 30 min; never poll in a loop.
- Max ~100 words per reply unless detail is asked for.
- Don't trust a number quoted in a log — re-derive it from the artefact's own columns.

## What is running right now

**Nothing.** `squeue -u o_iseri` is empty. All 224 campaign runs and 4 aggregations are COMPLETED;
the last job was the T9-13 resolver probe `1171061`, 2026-08-01 09:57.

Cluster root: `/speed-scratch/o_iseri/step8_4split/campaign/`.

| arm | jobs | model under test | aggregate | verdict |
|---|---|---|---|---|
| A | `1170493` 0–55 | T9-9 standby floor | `campaign/agg_A_t99` | closed |
| B | `1170493` 56–111 | + T9-10 lighting diversity | `campaign/agg_B_lm3` | closed — office `n=3` CONFIRMED, retail component REJECTED |
| C | `1170771` 0–55 | + T9-12 retail `lighting=calibrated_v2` | `campaign/agg_C_lm3v2` | closed — **current deliverable** |
| D | `1170771` 56–111 | + T9-11 `dhw=per_capita` | `campaign/agg_D_full` | closed — **T9-11 REFUTED, withdrawn** |

Injector md5 for arms A–D: `39a6e24e…` (`INJ_HASH=39a6e24e`). The cluster copy has since been
**overwritten** with the T9-13 build, md5 `9c2328ef7e70df058347b01fcde5a351` — so the next campaign
carries a different `INJ_HASH`, which is correct and must not be forced back.

## Where Step 9 actually stands

**Arms C/D verdict: 4 PASS, 1 FAIL.** P2 failed as written (office 0.101 %, hotel 0.081 % against a
pre-registered 0.05 % leakage threshold). **It was not relaxed.** The mechanism is thermal coupling —
retail lighting −20.6 % raises retail heating gas +14.6 %, and every off-retail delta is HVAC-only.

**T9-11 (occupancy-driven DHW rate) is dead.** It was killed by its own pre-recorded expectation:
the code comment predicted DHW falls in every channel; residential rose **+40.78 %**. Confirmed from
`dhw_hourly.csv`: night 00–05 share **8.34 % → 32.86 %**, peak draw hour **06:00 → 04:00**,
peak-to-mean 1.907 → 1.359, hourly max essentially unchanged (−2.41 %). The prototype's own night
share is 0.0358. Cause: it drove draw *rate* from instantaneous presence, and being home asleep at
04:00 is presence with no draw. Not residential-only — office −41.7 % with its peak halved.

**T9-13 (DHW volume scaling) replaces it. Written, tested, never simulated.**

```
f_new(t) = s_proto(t) · r(d)/R      r(d) = mean(occ_d) / mean(occ_ref_d)
Peak_Flow_Rate' = P · R             R    = max_d r(d)
```

The prototype's hourly shape passes through untouched, so peak hour and night share are preserved
*by construction*; daily volume scales exactly by `r(d)`; dividing the shape by `R` while
multiplying design flow by `R` keeps `max(f_new) = max(s_proto)`, so the Fraction bound never clips.
`r = 1` reproduces the prototype bit-for-bit. Hotel laundry no longer needs excluding — that closes
the "~54 % of design DHW still occupancy-invariant" item. 22/22 primitive tests pass, and the audit
`audit_dhw_shape_preservation` **has been seen failing** on T9-11's real output (D1+D2+D4); an empty
audit is a FAIL, not a vacuous PASS.

Two defects were found only by probing the real IDF, both of which would have shipped as **silent
whole-building no-ops**: (a) all 7 prototype DHW schedules are `SCHEDULE:YEAR`, not
`Schedule:Compact` — the resolver was extended to the full `Year → Week:Daily/:Compact →
Day:Interval/:Hourly/:List` chain and re-verified 7/7; (b) `reference="prototype_people"` is not
viable on this tower, which carries exactly one PEOPLE schedule for every channel,
`NECB-A-Occupancy`, with `mean_wd = 0.3583` and **`mean_we = 0.0000`** — `r_we = x/0` undefined, and
not commensurate anyway.

## Task 1 — build the reference table. Do this FIRST, before any decision.

`DHW_MODEL_VOLUME_SCALED["reference_occ_mean"]` ships **empty** on purpose: a channel missing from it
is reported `dhw_unresolved`, never defaulted to 1.0, because a defaulted reference fabricates a
no-op and reports it as a result.

Do **not** start by picking a baseline. Compute the per-channel weekly-mean occupancy for **every**
candidate reference in one pass and print the table — then the choice costs one line instead of a
re-run, and the sensitivity of `r` to the choice is visible *before* it is made.

Locally, `py -3`, reading `3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7/` (ignore every
`*_BAK_*` and `archive_pre_*` file):

| channel | file |
|---|---|
| office | `office_presence_multiplier_{2022,2030}.csv` |
| retail | `retail_presence_multiplier_{2022,2030_central,2030_cons,2030_opt}.csv` |
| hotel | `hotel_schedule_multiplier_{2022,2030_central,2030_cons,2030_opt}.csv` |
| residential | `BEM_Schedules_4split_{2022,2030_central,2030_cons,2030_opt}.csv` |

Historical years live under the Step-7 historical output dir — get the exact mapping from
`3rdJ_08D_campaign_cells.py:_build_scenarios()`, do not guess it.

Weekly mean must be built the same way `apply_dhw_volume_scaling` consumes it: a 24-value weekday
vector and a 24-value weekend vector per channel, means taken **time-weighted** over the 24 hours.
Report, per candidate baseline: `mean_wd`, `mean_we`, and the resulting `r_wd`, `r_we`, `R` for all
13 injected scenarios. **Flag any `R > 1.5`** — a large `R` means the water heater is resized, which
mixes a plant-sizing effect into what is meant to be a schedule lever, and would need its own
attribution arm.

## Task 2 — the specification decision, with my recommendation

**Recommendation: `Y2022`.** `{"tag": "Y2022", … "2022 observed cycle"}`,
`3rdJ_08D_campaign_cells.py:236-238`, all four channels present. The prototype's DHW volume is a
*present-day* engineering calibration, so the person-hours it is implicitly divided by should be the
*present-day* occupancy from the same series. Every 2030 bundle then reads as "person-hours relative
to today", and the historical panel reads as change from today with the correct sign.

`B_central` is the defensible alternative — it anchors on a *projected* future, so the observed year
Y2022 moves and the historical years get `r != 1` against a scenario that has not happened.

**`Default_NECB` is NOT a candidate, and the 2026-08-01 argument for it is struck.** It is declared
`{"channels": {}}` at `3rdJ_08D_campaign_cells.py:234` — no injection at all — so it is an exact
no-op under *every* reference (the property chose nothing), and it has no occupancy series of our
construction to take a mean of. That is exactly what makes it the control.

Carry this consequence: Y2005/Y2010/Y2015 carry **no hotel channel**
(`DELIBERATE_CHANNEL_EXCEPTIONS` — QC hotel ground truth starts 2019). Under a Y2022 reference hotel
is simply not injected there. Consistent, not a gap, but state it when reporting the hotel lever.

Two smaller choices, both recorded in the code and neither chosen by evidence:
- `peak_policy="rescale"` (current default) lets `Peak_Flow_Rate` rise with `R`. Physically
  consistent — more person-hours really is a larger design draw — but it changes plant design flow.
  `"cap"` forbids `R > 1`, preserving prototype sizing at the cost of under-serving busy scenarios.
- `r_max = 3.0` is a runaway guard, not a tuning knob. Any object hitting it is reported CLIPPED.

**Get the user's confirmation on the baseline before filling `reference_occ_mean`.** Everything
downstream is denominated in it.

## Task 3 — arm E, and write the predictions BEFORE launching

Arm E = arm C + T9-13 (`--lighting-model calibrated_v2 --dhw-model volume_scaled`), 56 runs, so
`E − C` is the pure DHW-volume effect with lighting held fixed. Same 56 cells, same throttle.

Order: fill `reference_occ_mean` → re-run the 22 primitive tests → `scp` the injector to
`/speed-scratch/o_iseri/step8_4split/campaign/repo/eSim_bem_utils/` and record the new md5 → run the
pre-flight validation job (the `3J_val_v2` pattern, job `1170770` is the template) → **write the
falsifiable predictions into the log** → `sbatch` the array → aggregate → analyse.

Integrity before any delta, not optional: identical 56 cell tags across arms,
`attribution_closed=True` everywhere, `max |area_E − area_C| = 0 m²`.

Predictions must include at least one that can kill T9-13, and at least one that distinguishes it
from T9-11. Suggested spine, to be sharpened with the real reference numbers in hand:
1. Night share and peak draw hour are **unchanged** in every channel — the identity T9-11 violated.
   `audit_dhw_shape_preservation` must return `pass=True` with a non-empty applied list.
2. Office DHW stops being flat across scenarios (it was 12.19 kWh/m² in every column to 2 dp in
   arm C) — with a *sign and magnitude* stated in advance, not just "it moves".
3. Hotel DHW now moves too, because laundry is no longer excluded — this is the direct reversal of
   arm D's P5, and it is the prediction most able to fail.
4. Residential DHW moves in the direction of the occupancy change and **does not** repeat +40.8 %.
5. Non-DHW end uses move only through thermal coupling — bounded, and the bound stated first.

## State of the gates — carry these forward honestly

| channel | band | status | note |
|---|---|---|---|
| office | [100,200] | **FAIL 0/56** | ~15 of the 22 kWh/m² shortfall is the standalone-prototype band, not the occupancy model (`Default_NECB` = 85.29 vs floor 100). Not expected to pass. |
| retail | [80,155] | **arm C: re-derive and record** | arm B's 56/56 PASS was rejected on mechanism (bought by freezing retail lighting). Arm C median EUI 90.05, freeze broken in all 4 geometry-city groups. |
| hotel | [180,300] | **FAIL 28/56** | bimodal: SuperTall 149–165 vs Tall 195–212, **nothing in [170,182)**. A median crossing 180 is an artefact of a median in an empty gap. |

No band, threshold or gate has been edited. The FAILs stand.

## Open items the user has not yet ruled on — Step 9 cannot close without these

- **Office gate**: recommendation on file is to verify, then demote `S9-EUI-office` to INFO and
  promote the exposure-ordering test in `3rdJ_09X_envelope_exposure.py` to PASS/FAIL.
- **Hotel gate**: recommendation is to split it by geometry (the band straddles an empty gap).
- **Retail NECB proxy** at `3rdJ_07_aug_to_bem_4split.py:20-45` — still provisional. T9-12 cut its
  weight from 100 % to 60 % but did not resolve it.
- **Leg-2 manuscript office EUI** is inflated ~1.706× by `calculate_eui()` missing a `ReportName`
  filter (`Leg2_2-split/Step8_docs/eSim_bem_utils_3J/plotting.py:293-299`). Leg-2 is read-only —
  this is a manuscript caveat to raise, not a file to edit.

## Provenance

Full detail, every number and every falsified prediction:
`3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md` (2313 lines).
Predecessor prompt: `improvements/prompts/3rdJ_L3_manager_prompt_2026-08-01.md`.
Memory: `project_3j_leg3_step9_status.md`.
