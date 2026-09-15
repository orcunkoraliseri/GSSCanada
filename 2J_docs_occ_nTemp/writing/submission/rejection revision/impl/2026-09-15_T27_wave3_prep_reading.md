# T27 — Wave 3 prep: reading pass on sampling, cell grid, envelope, static-arm machinery, metrics, wall clock — implementation state

Task doc:   this file (prompt given directly to this employee turn).
Plan:       `../00_REVISION_PLAN.md` §3 WP2, WP3, WP4, WP7.
Sources read: T05 (sample size), T16 (Step-8 machinery), T25 (Step-9 machinery), T17 (Speed reproduces
local), T19 + T22 (static arm), T21 (rerun), T03 (confidence intervals), T06/T07 (end use), plus direct
reads of `eSim_bem_utils_2J/main.py`, `08_simulation_plots.py`, `08_simulation_val.py`,
`enduse_hour_2022_v2.py`, `08_simulation.md`, `step8_array_v2.sh`, `step9_b_array_full.sh`,
`t21_array.sh`, and the `DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` file. Live `sacct` used for Q6
only (no jobs submitted).
Status:     DONE

## Ledger
Reading-only task. One live check: `ssh -o BatchMode=yes -o ConnectTimeout=60
o_iseri@speed.encs.concordia.ca "sacct -j 1328310 -X -n -o JobID,State,ExitCode,Elapsed,NCPUS"` (T22
static-arm array) — no jobs submitted, no writes to Speed.

## Verified

### Q1 — Household draw in `run_paired_mc.py` / `run_step8_paired_mc()`

- **Pool.** `pool = sorted(common or [])` where `common` = intersection, over every year in
  `--years`, of the household-ID keys of `schedules[y]` (`eSim_bem_utils_2J/main.py:2029-2034`).
  `schedules[y]` is loaded per year via `integration.load_schedules(csv_path, dwelling_type=dtype,
  region=region)` (`main.py:2025-2027`), i.e. **already filtered to the cell's archetype × province**
  before the pool is built — the pool is NOT the full 144,465-household stock, it is per-cell.
  Observed real pool size (MidRise × Ontario region, from a live job log): **9,376**
  (`impl/T19_out/logs/t19_smoke_1328297.out:63`, `"Pool=9376 sampled=2 replacement=False"`).
- **Draw.** `rng = random.Random(_step8_cell_seed(seed, cell_label))`; `sampled = rng.sample(pool, n)`
  without replacement if `len(pool) >= n`, else `rng.choice()` per slot with replacement
  (`main.py:2040-2047`). `_step8_cell_seed()` derives a per-cell seed from SHA-256 of
  `f"{archetype}__{city}"` mixed with the base seed (`main.py:1952-1962`); base seed defaults to 42
  (`Step8_docs/run_paired_mc.py:38`). **Seed is per cell, not global** — every cell gets its own
  deterministic RNG stream, but all cells share the same base seed=42.

**(a) Does n=200 start with the same 50 as n=50?**
Tested locally (`py -3`) replicating the exact call, `random.Random(seed).sample(pool, k)`, at both the
observed real per-cell pool size (9,376) and the full-stock size (144,465), seed=42:
```
pool_size=9376:   n=50 first5=[1824,409,4506,4012,3657]; n=200 first5=[1824,409,4506,4012,3657]
                  n=50 == first-50-of-200 (ORDER):  True
pool_size=144465: n=50 first5=[29184,6556,72097,64196,58513]; n=200 first5=[same]
                  n=50 == first-50-of-200 (ORDER):  True
```
**Yes, at both pool sizes, in this campaign, the n=200 draw's first 50 elements are byte-for-byte, in
order, identical to the standalone n=50 draw.** Reason, from the CPython `random.sample()` algorithm
itself: `sample()` picks one of two internal algorithms by comparing the population size `n` to a
threshold `setsize` computed **from the requested k** (`setsize = 21` if `k<=5`, else
`21 + 4**ceil(log4(3k))`). For k=50, `setsize=277`; for k=200, `setsize=1045`. Both pool sizes in this
campaign (9,376 and 144,465) are far larger than either threshold, so **both the k=50 and the k=200
call use the same branch** — a sequential rejection-sampling loop (`j = _randbelow(n); while j in
selected: j = _randbelow(n); selected.add(j); result[i]=population[j]`) whose i-th draw depends only on
the RNG stream and `n`, never on the target `k`. Because both calls share the same seed, the same `n`,
and the same algorithm branch, the sequence of accepted indices is identical step-by-step, so the first
`min(k1,k2)` results are a common prefix regardless of `k`. This would **not** hold if the pool were
small enough (roughly pool ≲ 1,045 for a k=200 call) to trip CPython into its other branch (partial
Fisher–Yates over a copied list) for one k but not the other — not the regime any cell in this campaign
is in (smallest observed pool 9,376 ≫ 1,045).
Test script: local scratchpad `t27_sample_test.py`, run with `py -3` (not on Speed, per task rules).

**(b) `--years 2030` alone vs `--years 2022,2030`, same-ID 2030 file.**
From the code (`main.py:2029-2034`): the pool for `--years 2030` alone is `sorted(keys(schedules['2030']))`
(no intersection needed, one year); the pool for `--years 2022,2030` is
`sorted(keys(schedules['2022']) & keys(schedules['2030']))`. **If the 2030 file's household-ID set is
identical to the 2022 file's** (the question's premise), the intersection equals either set, so both
pools are the same sorted list of IDs. The RNG seed depends only on `_step8_cell_seed(base_seed,
cell_label)` (`main.py:1952-1962`), which does **not** depend on `--years` at all. Same pool + same seed
→ `rng.sample(pool, n)` returns the identical draw either way. **So yes, from the code, the draw is
identical in that specific case** — but only because the premise (identical ID sets) makes the pools
equal; in general (e.g. the real 2022/2030 files, which differ by ~42 HH per T16 Q2) the two calls draw
from different pools and can select different households.

**(c) E+ runs per household per year.**
**One** run per `(sample, year)` for the Step-8 main model: the loop `for y in years:` builds exactly one
`Scenario_{y}.idf` / one job per year per sampled household (`main.py:2059-2072`). (Step 9 is a separate
campaign that runs the SAME household through 2 arms — baseline and activity — per year, i.e. 2 runs per
household per year there; T25 Q2, `2026-09-15_T25_step9_run_machinery.md`.)

### Q2 — Cell list

- **4 archetypes** (exact strings used in cell names): `SingleD`, `OtherDwelling`, `MidRise`,
  `HighRise`. **6 cities**: `Toronto_5A`, `Kelowna_5B`, `Vancouver_5C`, `Montreal_6A`, `Calgary_6B`,
  `Winnipeg_7A`. Cell label = `f"{archetype}__{city}"`.
- **Order** (`Step8_docs/step8_array_v2.sh:18-29`, `Step9_docs/step9_cluster/step9_b_array_full.sh:31-38`,
  `impl/T21_scripts/t21_array.sh` header, all three identical): archetype is the OUTER loop (6-task
  blocks in the fixed order SingleD, OtherDwelling, MidRise, HighRise), city is the INNER loop, always
  in the order Toronto, Kelowna, Vancouver, Montreal, Calgary, Winnipeg. So task index = `archetype_idx*6
  + city_idx` (0-based).
- **Montreal task ids** (`Montreal_6A` is city index 3):
  - 24-cell arrays (`step8_array_v2.sh`, and `t21_array.sh` per campaign, one array per campaign): task
    **3** = `SingleD__Montreal_6A`, **9** = `OtherDwelling__Montreal_6A`, **15** = `MidRise__Montreal_6A`,
    **21** = `HighRise__Montreal_6A`.
  - 48-task Step-9 array (`step9_b_array_full.sh`, task 0-23 = baseline, 24-47 = activity,
    `CELL_IDX = SLURM_ARRAY_TASK_ID % 24`): baseline Montreal tasks **3, 9, 15, 21**; activity Montreal
    tasks **27, 33, 39, 45** (24 + the same four cell indices).

### Q3 — Envelope

- **Same base IDFs, local and Speed.** T16 Q3 / T17 confirmed the archetype IDF files come from
  `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/` on both local Windows runs and Speed (path resolves
  relative to wherever `eSim_bem_utils_2J/main.py` sits, `main.py:38-39`; T17 staged the identical files
  and reproduced local results to <0.001%). SingleD = `DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf`.
- **Wall construction actually used (`NBC936_Z6_Wall`)**, this IDF:
  `Construction, NBC936_Z6_Wall, 1IN Stucco / 8IN CONCRETE HW / NBC936 Z6 Wall Insulation / 1/2IN Gypsum`
  (`...v242.idf:2283-2288`). Insulation layer material: `Material, NBC936 Z6 Wall Insulation,
  MediumRough, Thickness 0.215 m, Conductivity 0.049 W/m-K` (`...v242.idf:2004-2010`; R of this layer
  alone ≈ 0.215/0.049 ≈ 4.39 m²K/W, ~RSI-4.4 / R-25 imperial, before adding stucco/concrete/gypsum
  layers). Roof insulation `NBC936 Z6 Roof Insulation`: thickness 0.416 m, conductivity 0.049 W/m-K
  (`:2015-2018`, RSI ≈ 8.5). Foundation/slab insulation: thickness 0.13 m / 0.117 m, same conductivity
  0.049 (`:1949-1955`, `:1982-1988`). Window: `WindowMaterial:SimpleGlazingSystem, NBC936 Z6 Window
  Glass, U-Factor 1.6 W/m2-K, SHGC 0.4` (`:2075-2077`).
- **Infiltration is NOT a `ZoneInfiltration:*` object — no such object exists in this IDF** (grepped
  `nfiltration|irflow|entilation` case-insensitively, zero `ZoneInfiltration` hits). Infiltration/leakage
  is modelled through an **AirflowNetwork** (`AirflowNetwork:SimulationControl, House AirflowNetwork,
  MultizoneWithDistribution, SurfaceAverageCalculation wind-pressure model, LOWRISE`, `:3274-3290`), with
  per-surface **Effective Leakage Area (ELA)** objects, e.g. `ZoneLeak_LongWall` ELA 0.002361 m²,
  `ZoneLeak_ShortWall` 0.001771 m², `ZoneLeak_Ceiling` 0.008291 m², `ZoneLeak_Floor` 8.33e-6 m²,
  `AtticVent`/`CrawlVent` 0.37 m² each (all discharge coeff. 1.15, reference ΔP 4 Pa, flow exponent 0.65)
  (`:3513-3560`). **No single ACH/flow-rate number exists for this archetype — there is no code anywhere
  that sets a bulk ACH; infiltration is whatever the AirflowNetwork solver computes from these leakage
  areas plus zone pressure differences.** No runtime Python sets any of this (confirmed independently,
  T16 Q6: grepping `infiltration`/`Construction` in `Step8_docs`/`eSim_bem_utils_2J` found only an
  unrelated plot-legend colour string) — the envelope is baked into the IDF file itself, not computed
  or swapped by code.
- **Older-vintage / pre-code envelope variant: NOT FOUND.** The repo does hold two other building sets,
  neither of which is a pre-code/leakier vintage: (1) `BEM_setup/Buildings_CLG/` — "cold-zone envelope
  sensitivity," the SAME 4 archetypes rebuilt to **Z7A code** (a colder, MORE stringent code requirement
  for Calgary/Winnipeg), described as "available (optional)" (`08_simulation.md:38,51`) — this is a
  stricter, not older, envelope. (2) `ASHRAE_HighRise_ST15/ST20` — height variants for a HighRise
  sensitivity, not a vintage/insulation change (`08_simulation.md:51`). Grepping the whole
  `2J_docs_occ_nTemp` tree for vintage/pre-1980/pre-code/R-2000/construction-swap language found no
  older-stock envelope, no infiltration-vintage table, and no code path that swaps construction objects
  by vintage. A WP7-C older-stock arm would need a **new** IDF variant (or hand-edited construction
  objects) — nothing existing can be pointed at it.

### Q4 — Static-schedule arm machinery (`run_static_arm.py`, T19/T22)

- **Injection mechanism.** The wrapper calls the SAME `run_step8_paired_mc()` used by the real campaign,
  passing `years=['static']` and a pre-built `schedules={'static': <dict>}` argument
  (`2026-09-15_T19_wp3_static_arm_build_smoke.md` Decisions) — no pipeline source edited. This reaches
  the same `integration.inject_schedules()` call as the main model (`integration.py:1269-1305`, called
  from `main.py:2065-2070`), which injects **occupancy** (`Schedule:Compact` named
  `Occ_Sch_HH_{hh_id}`), **equipment** (`ELECTRICEQUIPMENT`, per-zone, `Design_Level=equip_design_w`) and
  **lighting** (`LIGHTS`, per-zone, `Lighting_Level=light_design_w`) (`integration.py:1411,1447-1448,
  1616-1622,1707-1712`). **DHW is not wired into this single-building path at all** (confirmed by grep,
  no DHW hookup found in `inject_schedules()` — T16 Q4/Q5, T19 Verified) — the static arm cannot and does
  not touch DHW because the main model doesn't either.
- **Where the static values come from.** `idf_optimizer.load_standard_residential_schedules(baseline=
  'midrise')` (`idf_optimizer.py:570-624`), reading `0_BEM_Setup/Templates/schedule.json` — a DOE
  MidRise / OpenStudio-Standards "ASHRAE 90.1-compliant" 24 h weekday/weekend profile, same profile used
  for every archetype (the main model also uses the MidRise baseline for all archetypes, per the T19
  Design section). Mapping into the campaign's `schedule_data` dict format is index-for-index by hour:
  `occupancy[h]->occ`, `equipment[h]->equip_frac`, `lighting[h]->light_frac`, the scalar `activity`
  value repeated 24× `->met` (T19 Verified — Step 1). **A real bug found and routed around, not fixed
  (out of scope):** `idf_optimizer.py:625`'s own `base_dir` is only 2 `dirname()` levels up from
  `idf_optimizer.py`, not `main.py`'s 4-up `BASE_DIR` — on the real repo layout this path never resolves,
  so **every unedited call to `load_standard_residential_schedules()` anywhere in the pipeline silently
  falls back to a hardcoded approximation**, not the real `schedule.json`, and the one warning it would
  print is suppressed by default (`verbose=False`). T19/T22 worked around it by staging a copy of
  `schedule.json` at the buggy-but-unedited 2-up path inside their own code tree — this is a real,
  live pipeline defect worth a fix ticket.
- **Flags.** `run_static_arm.py --archetype --city --n --seed --sched-dir --output-dir --code-root`, plus
  a `--check-only` mode (T19 Brief step 2/3). `--code-root` must point at a T17-style staged tree (`main.py`'s
  `BASE_DIR` is not otherwise overridable).
- **Could the same wrapper take a per-archetype, per-year mean at-home profile instead?** Yes,
  architecturally — the swap point is identical: build a `schedules={'<label>': {hh_id: {...}}}` dict
  the same shape `integration.load_schedules()` returns, but instead of every household getting the SAME
  fixed `schedule.json` profile, every household in a given archetype × year would get the SAME
  **computed mean** occupancy/equipment/lighting 24 h weekday+weekend profile for that archetype/year
  (averaged across the real households' diaries), while `equip_design_w`/`light_design_w` (SHEU levels)
  stay per-household exactly as the static arm already does. What would need to change: (1) a new
  function (does not exist yet — T16 Q5 explicitly: "no function found that averages across households
  into one representative profile... NOT FOUND as an existing function") that computes the mean
  `occ`/`equip_frac`/`light_frac` per hour across a cell's real per-household diaries for one archetype
  × year; (2) `run_static_arm.py`'s schedule-source line swapped from
  `idf_optimizer.load_standard_residential_schedules()` to this new averaging function, called once per
  archetype × year and broadcast to every sampled household's dict entry; (3) the wrapper's `years=`
  label changed from `'static'` to something like `'avg_{year}'` per archetype so outputs land under a
  distinct dir; everything else (the `run_step8_paired_mc()` call, injection, output layout) is reused
  unchanged.
- **"SHEU scaling" in the main model, and in the static arm.** Equipment/lighting `Design_Level` values
  are set from the household's SHEU-calibrated `equip_design_w`/`light_design_w` fields inside
  `inject_schedules()` (`integration.py:1584,1755-1758,1836-1840`, replicated per zone for multi-zone
  archetypes). **Applied identically in the static arm**: `equip_design_w`/`light_design_w` are read
  straight off the real per-household `BEM_Schedules_2022.csv` row and left untouched — only the four
  hourly-fraction keys (`occ`/`equip_frac`/`light_frac`/`met`) are swapped for the static profile (T19
  Verified/Decisions: "SHEU design levels stay per household... falls out for free from building the
  static dict on top of `integration.load_schedules()`'s own real-CSV output"). Confirmed in the T19
  smoke run's own numbers: two households' design levels differed (711.65 W / 133.78 W vs 996.8 W /
  135.0 W) while both got the identical static occupancy curve (T19 collector Verified).

### Q5 — Metric definitions and weighting

- **Annual kWh**: `Electricity:Facility` meter (site total, already includes lights+equipment+fans —
  never add components to it) (`08_simulation_plots.py:79` meter constant `FACILITY`, comment
  "site electricity TOTAL (already includes lights+equip+fan)"; summed at `:361`/T05 Verified).
- **Peak demand**: `peak_kW_annual = flat.max()` (single hottest hour of the year) and
  `mean_daily_peak_kW = daily_peak.mean()` (mean of the 365 daily maxima) — both in the WP6 script,
  `impl/T06_scripts/enduse_hour_2022_v2.py:295-298` (adapted from `08_simulation_plots.py`'s own
  `amax`/`max24` computation at `:295,375`).
- **Peak hour**: reported as `mean_peak_hour`, the **circular mean of the 365 daily-peak hours**
  (`_circular_mean_hour`, `08_simulation_plots.py:278-285`, computed per household at `:372,378,388`) —
  this is the definition the paper's own stock-weighted figure uses, not the single annual-max hour
  (`peak_hour_annual`, also computed, `:375`, but not used for the headline number — T05 Decision D-T05-1,
  manager-accepted).
- **Load factor**: `mean24 / max24` — mean hourly facility load over the peak hourly facility load
  (`08_simulation_plots.py:385`, `enduse_hour_2022_v2.py:300`).
- **Midday share**: facility electricity summed over hours 9-17 (`MIDDAY=(9,17)`,
  `08_simulation_plots.py:114`) divided by the annual total (`:387`, `enduse_hour_2022_v2.py:301`).
- **Evening ramp**: `facility_kW[17] - facility_kW[14]` per day, then the **mean over 365 days**
  (`evening_ramp_kW_mean`) and its 90th percentile (`evening_ramp_kW_p90`) — `enduse_hour_2022_v2.py:
  302-305`. This metric does **not** exist in the paper's original `08_simulation_plots.py` — it was
  built new for WP6/WP3 (T06).
- **Household peak-hour spread**: **NOT FOUND** as a coded/computed metric anywhere (searched
  `08_simulation_plots.py`, `enduse_hour_2022_v2.py`, and the wider repo for "peak-hour spread",
  "peak_hour_spread", "morning-peak minority"). The plan's "22-25% morning-peak minority" language
  (`00_REVISION_PLAN.md:214`) is a qualitative description, not a defined/coded statistic yet — WP3
  would need to define and implement it (e.g. the spread/std of `mean_peak_hour` across the 50
  households in a cell, or the fraction of households whose `mean_peak_hour` falls in a morning window).
- **Stock weighting — confirmed as T05 reported.** `STOCK_WEIGHTS` = archetype-only, `{SingleD: .529,
  MidRise: .213, OtherDwelling: .130, HighRise: .128}` (renormalized over 4 archetypes,
  `08_simulation_plots.py:74-77`); no province-level weight exists anywhere in the code.
  `_stock_weighted_circular_mean()` splits each archetype's weight equally across its (up to 6) cities,
  `w_each = STOCK_WEIGHTS[arch] / len(sub)` (`:300-321`, read directly, matches T05's citation exactly).
- **Confidence intervals (T03).** Code: `2J_docs_occ_nTemp/08_simulation_val.py:951-1027`,
  `SimulationValidator.validate_shift_effect`. Method: household-paired (`sim_hh_id` matched between 2022
  and 2030 rows, inner join, `:957-961`), delta = 2030−2022 per household (`:963-967`), **pooled flat and
  unweighted across all 24 cells** (no per-cell averaging, no stock weight), then a **parametric
  one-sample Student-t interval** on the pooled deltas (`scipy.stats.t.interval(0.95, len(d)-1,
  loc=mean, scale=sem)`, `:973-975`) — not a bootstrap, no replicates, no seed. T03's own reproduction
  job (1328238/1328253) found the submitted CI numbers (+0.367 pp / +0.0117) do **not** reproduce from
  either surviving `agg_annual.csv` copy (July or June); the source file is lost. A cell-stratified
  cluster bootstrap alternative changes interval width by only ~1-4% either direction — not a
  qualitative difference from the t-interval.

### Q6 — Wall clock (from live `sacct`, no jobs submitted)

- **Main model (T17, job 1328286), 50 households × 2 years = 100 E+ runs/cell, 8 CPUs/task:**
  SingleD 14m13s, OtherDwelling 36m11s, MidRise 2h35m55s, HighRise 1h34m14s. Runs/CPU-hour: SingleD
  ≈ 52.7, OtherDwelling ≈ 20.7, MidRise ≈ 4.8, HighRise ≈ 8.0 (single-zone SingleD is far cheaper than
  the multi-zone apartment archetypes).
- **Static arm (T22, job 1328310, live check this turn), 50 households × 1 static profile = 50 E+
  runs/cell, 4 CPUs/task:** SingleD tasks (0-5, all 6 cities) COMPLETED 24m52s-26m38s (avg ≈25.6 min);
  OtherDwelling tasks (6-11) COMPLETED so far 37m20s-59m07s (2 of 6 still running/pending at check time).
  Runs/CPU-hour: SingleD ≈ 29.4, OtherDwelling (58-59 min cities) ≈ 12.8-12.9. As of this check
  (2026-09-15), 9/24 static-arm tasks COMPLETED, 2 RUNNING, 13 PENDING — job not finished, no polling
  done beyond this one status read.

## Decisions
- **D-T27-1 (assumed).** For Q1a, used the observed real per-cell pool size (9,376, from a live job
  log) as the "per-cell pool size" the task asked to find, rather than inventing or estimating one —
  this is the only concrete per-cell pool number on record in any read doc or log.
- **D-T27-2 (assumed).** For Q3, treated "older-vintage / pre-code envelope variant" strictly (a
  less-insulated, leakier construction set) and did not count `Buildings_CLG` (a stricter Z7A
  cold-climate code variant) or the HighRise height variants as satisfying it, since both move envelope
  performance in the opposite direction from what WP7-C needs. Flagged as NOT FOUND rather than citing
  a near-miss as if it qualified.
- **D-T27-3 (assumed).** For Q5's "household-level peak-hour spread," reported NOT FOUND as a coded
  metric rather than defining one myself — the task said answer with file:line or NOT FOUND, and
  inventing a definition here would preempt a manager/WP3 design choice.
- **D-T27-4 (assumed).** For Q6, used the T22 static-arm job's mid-flight `sacct` state (9 of 24 tasks
  COMPLETED at check time) rather than waiting for it to finish, per the task's own hard rule ("do not
  submit jobs") and the general no-polling/no-waiting rule — reported exactly what was COMPLETED, RUNNING,
  or PENDING at the one live check, not projected/extrapolated numbers for the unfinished cities.

## Next
Reading task complete; no code changed, no jobs submitted. Manager: Q3's confirmed absence of an
older-vintage envelope variant means WP7-C (envelope sensitivity) needs a new IDF/construction set, not
a config swap. Q4's `idf_optimizer.py:625` `base_dir` bug (2-up vs main.py's 4-up `BASE_DIR`) silently
disables the real DOE-MidRise schedule fallback pipeline-wide and is worth its own fix ticket, separate
from Wave 3. Q5's CI-source-file loss (T03) already flagged in T03's own doc; repeating here since WP8's
rewrite depends on it. Q6's T22 static-arm job (1328310) was still running at check time — a fresh
collector can re-run the same `sacct` command later for the remaining MidRise/HighRise timings.

## WHAT I DID NOT VERIFY
- Did not independently re-derive the CPython `random.sample()` source (the two-branch algorithm
  description in Q1a is from documented/known CPython `Lib/random.py` behaviour, not re-read from a
  local Python installation's own `random.py` source file in this session) — verified its *behaviour*
  empirically (the local `py -3` test), not its *implementation* by reading `random.py` itself.
- Did not check whether every one of the 24 cells' real per-cell pool sizes are all ≫ 1,045 (the k=200
  branch threshold) — only confirmed one observed pool size (9,376, MidRise/Ontario) and the full-stock
  size (144,465); did not enumerate all 24 archetype×province pool sizes from `BEM_Schedules_2022.csv`
  directly (would require a Speed/local Python read of a large CSV, out of scope for a reading-only
  task with no cluster jobs).
- Q1b's answer is conditional on the question's own premise ("a 2030 file holding the same household
  IDs") — did not check whether the REAL `BEM_Schedules_2030.csv` on disk actually has the same ID set
  as `BEM_Schedules_2022.csv` (T16 Q2 already documents they differ by ~42 HH on the current frame, so
  the real-world answer to "are the pools identical today" is NO — only the hypothetical in the question
  was answered from the code).
- Q3's U-value/RSI arithmetic (e.g. "~RSI-4.4") is a hand computation from the single insulation layer's
  thickness/conductivity only — did not compute the full assembly R-value including the stucco/concrete/
  gypsum layers, air films, or the window's full NFRC-style U-value context; reported as the insulation
  layer alone, not a certified whole-assembly U-value.
- Did not open `AttachedHouse`/`ApartmentMidRise`/`ApartmentHighRise` IDFs for their own construction/
  infiltration objects — Q3 was answered from the SingleD (`DetachedHouse`) IDF only, per the question's
  own "SingleD envelope" framing; the other 3 archetypes were not individually confirmed to use the same
  AirflowNetwork-vs-ZoneInfiltration pattern (T16 Q6's repo-wide grep suggests they do, but this was not
  re-verified per-archetype in this pass).
- Did not re-derive T17's/T22's `sacct` elapsed times myself beyond the one live re-check for T22
  (1328310) — T17's numbers (Q6) are taken verbatim from `2026-09-15_T17_speed_reproduces_local_
  campaign.md`'s own already-collected `sacct` output, not re-queried live in this session.
- Did not build or test the "per-archetype per-year mean at-home profile" averaging function described
  in Q4 — described the required change from reading the existing code architecture, did not write or
  run any new code (out of scope: this is a reading task).

## Manager note (2026-09-15, after reading)
- Q5 "household peak-hour spread: NOT FOUND" is superseded: the paper's code has it. Mardia circular SD
  `_circular_sd_hours` (`Step8_docs/08_simulation_plots.py:290`) and the "morning-leaning" share, circular mean
  daily-peak hour in `[0, 12)` (`08_simulation_plots.py:914-915`). The search missed it because the code says
  "morning-leaning", not "morning-peak". Used in T30.
- Q4 schedule fallback bug: T23 already found the fallback values numerically identical to `schedule.json`, so no
  published number changes. No fix ticket in this revision; Wave 3 trees keep staging `schedule.json`.
- Wave 3 docs written from this reading: T28 (WP4 N=200), T29 (WP2 scenario runs), T30 (WP3 average profile),
  T31 (WP7.3 envelope).
