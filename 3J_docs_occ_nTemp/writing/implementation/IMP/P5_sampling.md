# P5 — What is sampled, and how noisy the results are

Scope executed: plan Section 5 "P5", steps 1-2 only (no seed-replicate runs; that is V3a, a
separate agent). Read: Step5/6/7 scripts under `Leg3_4-split/`, the cell `manifest.json` files in
`Leg3_4-split/Step8_docs/campaign_local_deliverable/`, and (traced from the manifest's own `seed`
field) the actual injector function in `eSim/eSim_bem_utils/commercial_integration.py`, which lives
outside `Leg3_4-split/` but is the only place the per-apartment draw is coded — flagged clearly
below as outside the stated Step5-7 scope.

## What is drawn, stage by stage

**Stage 1 — Step 5, one donor diary per census person (population-wide, not per tower).**
`run_slot_match()` draws ONE diary row per Census agent from the GSS pool, via
`np.random.choice(cand)` inside a per-agent loop —
`Leg3_4-split/Step5_docs/3rdJ_05_censusLinkage_4split.py:449`. The RNG is seeded once at function
entry, `np.random.seed(int(os.environ.get("STEP5_MATCH_SEED", "42")))` —
`3rdJ_05_censusLinkage_4split.py:391` — default 42, documented as "byte-identical to every run made
before 2026-08-05" (`:386`). This runs over the FULL deduplicated Census file (all agents, not
city- or tower-specific) — `run_linkage_full()`, `:949-983`; the file is
`0_Occupancy/Outputs_Aligned/Aligned_Census_2025.csv` (`:63`). Day-type (weekday/weekend) is
assigned by a second, independently-seeded draw, always seed 42, never reseeded via env var:
`_assign_dday(df_census, seed=42)` (`:980`, function at `:568-574`, `rng = np.random.default_rng(42)`
at `:572`). **One realisation**: both draws run once per pipeline build; nothing in Step 5 draws
more than one diary per agent.

**Stage 2 — Step 6, population-level 2030 scenario construction.**
`build_cycle_pairs(seed=42)` (`Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split.py:599`,
called at `:717`) internally reseeds per cycle-pair: `rng = np.random.default_rng(seed=src_i * 3 +
s_tgt)` (`:637`) — a deterministic function of which two survey cycles are being paired, not a free
seed. The WFH-band reweight `_posthoc_reweight(..., rng_seed=42)` (`:1923`, draw logic `:1968-1999`)
is called once per band with a DIFFERENT seed per band —
`rng_seed={"conservative": 42, "hybrid": 43, "fullyhybrid": 44}[band]` (`:2092`) — so the three
office bands (cons/central/opt) are three distinct, non-overlapping draws, not the same draw
filtered three ways.

**Stage 3 — Step 7, per-cell-family product assembly (still population-level, not per-tower).**
Header states `seed=42 throughout` (`Leg3_4-split/Step7_docs/3rdJ_07_aug_to_bem_4split.py:57`).
Three separate `np.random.default_rng(42)` calls, all fixed at 42 regardless of scenario or city:
`complete_day_types()` (`:355`, fills the missing day-type for census-linked households that got
only one day-type from Step 5, via `rng.integers(0, len(we_pool)/len(wd_pool), size=len(sub))`,
`:367`/`:377`); `assemble_2030()` (`:394`, random pool draw per DDAY_STRATA stratum, `:410`,
documented as unsuitable for Office because it destroys the occupation signal — see the measured
comparison at `:481-486` — kept only for Residential); `demo_assemble_2030()` (`:514`, tiered
occupation-matched draw for Office, `rng.integers(len(arr))` at `:539`, one candidate chosen per
stock row).

**Stage 4 — Step 8 injector, per-tower household assignment (the actual "how many per tower").**
`RESIDENTIAL_SEED = 42`, "pinned explicitly on every cell rather than relying on the injector's own
default" — `Leg3_4-split/Step8_docs/3rdJ_08D_campaign_cells.py:168-170`, wired into every
non-`Default_NECB` scenario at `:178`, `:190`. The actual draw:
`draw_residential_households(pool, n, seed=42)` —
`eSim/eSim_bem_utils/commercial_integration.py:1847-1865` — sorts all eligible SIM_HH_ID values
numerically first (`:1857`, so dict iteration order can never affect the result), then
`rng = np.random.default_rng(seed); idx = rng.choice(len(hh_ids), size=n, replace=False)`
(`:1863-1864`): **n DISTINCT households, no replacement**, one per residential apartment Space.
`n` = the tower's own apartment count, read from the IDF's `SPACE` objects (`:1909-1914`), NOT a
fixed number — confirmed from the manifests: `campaign_local_deliverable/B_central__Tall__MTL/manifest.json`
"`n_households_drawn`": 27; `B_central__SuperTall__MTL/manifest.json`: 41.

## How many per tower, and whether cells share draws — measured from the manifests

- Tall towers draw 27 households; SuperTall towers draw 41 (both cities, all scenarios that carry
  residential — confirmed for `B_central`, `Y2022` in
  `campaign_local_deliverable/*/manifest.json` `inject_mixed_use_result.residential.n_households_drawn`).
- **MTL and CLG share the identical household draw.** `B_central__Tall__MTL/manifest.json` and
  `B_central__Tall__CLG/manifest.json` both read the SAME residential CSV
  (`csv_md5 = d36388c8958f4f3ac72f5e9ae508c711`, `BEM_Schedules_4split_2030_central.csv`) with the
  SAME `seed: 42`, and their `assignment` blocks (space name -> household ID) are byte-identical —
  verified by diffing the two manifests' `assignment` dicts (27 entries each, 0 differences). This
  follows directly from the code: same `pool` (same CSV -> same sorted `hh_ids`), same `n` (same
  tower geometry), same `seed` -> `rng.choice` returns the same indices every time
  (`commercial_integration.py:1848-1851`, "Same seed -> same draw, every time"). So **the two cities
  in a scenario/tower pair are NOT independent realisations of the residential population** — they
  see the same 27 (or 41) synthetic households, only the Office/Retail/Hotel multiplier curves
  differ by province.
- **Office is also shared nationally, not by province.** The Office product carries no `pr` field in
  the manifest at all (only `archetype`/`band`) and its `csv_md5` is identical across MTL and CLG —
  confirmed for `B_central__Tall__CLG` vs `B_central__Tall__MTL`. Retail and Hotel DO carry a `pr`
  field (`QC` for MTL, `AB` for CLG) and are filtered from the same underlying CSV
  (`retail_presence_multiplier_2030_central.csv`, identical md5 `cf8721c62030fc7c1f23b999f85056d0`
  for both cities) by province.
- Scenarios (`B_central` vs `Y2022`) draw from DIFFERENT source CSVs
  (`BEM_Schedules_4split_2030_central.csv` md5 `d36388c8...` vs `BEM_Schedules_4split_2022.csv` md5
  `281d96c0...`), so they are independent populations, but every scenario still uses the same
  `seed=42`, so the within-scenario MTL/CLG sharing above holds for every scenario.
- `Default_NECB` cells carry `n_households_drawn: 0` (no residential injection — code-schedule
  control, confirmed in `Default_NECB__Tall__MTL/manifest.json`).
- **One realisation only.** Nowhere in Steps 5-8 does the shipped pipeline draw more than one
  synthetic population per cell; every seed above is a single fixed integer (42, or 42/43/44 by
  band), never swept, in the frozen deliverable.

## Seed handles

Every place a seed could be changed to produce an independent replicate, cheapest first:

1. **CHEAPEST — `RESIDENTIAL_SEED` in `3rdJ_08D_campaign_cells.py:168`** (or the `seed` argument
   passed into `draw_residential_households()`/`inject_residential()`,
   `commercial_integration.py:1847`/`:1868`). Changes only WHICH 27/41 households are assigned to
   apartments and their apartment-to-apartment order. Nothing upstream of Step 8 needs to rerun:
   Steps 5-7's population products are untouched (they are read, not regenerated), so a replicate
   costs one Step-8 injection + one EnergyPlus run per affected cell. No GPU, no retraining. This is
   the handle V3a should use.
2. `STEP5_MATCH_SEED` env var, already wired at `3rdJ_05_censusLinkage_4split.py:391` for exactly
   this purpose ("V2-E4c multi-draw sweep", comment at `:385-389`) — reseeds the Stage-1 donor
   draw. Changes the whole population's diaries, so Steps 6-8 must all rerun. More expensive than
   (1) and changes a different thing (which diary each person carries, not which tower gets which
   household).
3. `rng_seed` in `_posthoc_reweight()`, Step6 `3rdJ_06_longitudinalForecasting_4split.py:1923`
   (currently 42/43/44 by band) — reseeding changes the 2030 WFH-day cohort composition. Requires
   Step 6 through Step 8 to rerun.
4. `seed` in `_assign_dday()`, Step5 `:568`/`:980` — hardcoded, not env-overridable as shipped;
   changing it changes which days are called weekday/weekend for every agent. Full Step 5-8 rerun,
   and touches the census-side population the Step-5 docstring says is deliberately held fixed as a
   "lower bound on total draw noise" (`:387-389`) — changing it would break that design intent, not
   just add noise.
5. Step 5's `sample_frac`/`random_state=42` (`:762`) only affects the SMOKE run (1% sample), not the
   full/deliverable pipeline (`run_linkage_full()` uses the full deduplicated Census with no
   sampling) — not a usable handle for a paper-relevant replicate.

## Two draft Methods sentences

Each simulated cell's residential population is one realisation: for each tower, N distinct
synthetic households (27 for the Tall prototype, 41 for SuperTall) are drawn without replacement,
seed 42, from the scenario's population-level household pool, and the two cities within a
tower/scenario pair are assigned the identical set of households, so any Montreal-Calgary
difference in the reported results reflects the office/retail/hotel provincial multipliers and
building geometry only, not an independent residential draw. Run-to-run sampling noise in the
residential channel has not been measured from repeated draws in the frozen deliverable; a cheap
seed-replicate check (re-drawing the household set with a different seed, no upstream retraining)
is reported separately if run.
