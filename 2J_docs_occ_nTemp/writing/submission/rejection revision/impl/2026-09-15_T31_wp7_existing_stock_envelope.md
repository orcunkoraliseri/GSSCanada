# T31 — WP7 step 3: single-detached rerun with an existing-stock envelope, 2022 and 2030 — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP7 step 3, §7 D3, §10 Wave 3.
Facts used: `2026-09-15_T27_wave3_prep_reading.md` Q3 (envelope is baked into the IDF, no older variant exists,
infiltration is an AirflowNetwork of leakage areas), T07 (end-use breakdown 2022), T21 (engine, paths).
Values from: `../deepResearch/dr_2J-09_existing_stock_envelope_prompt.md` (run by the author; not yet returned).
Status:     SMOKE PASS (phase A complete) -- job 1328400 COMPLETED exit 0, E0/E1/E2 all confirmed on real E+ output; phase B waits for vetted values

## Design (manager, fixed before any result)
- **Which envelope (manager, 2026-09-15).** The plan says "older-stock (pre-code)". Decided instead: the
  **existing single-detached stock average**, because the benchmark it is compared to (SHEU 2019, Table 5 of
  the submitted paper) describes the existing stock. A pre-1980 envelope would overshoot on purpose and prove
  less. One envelope only, SingleD only (D3).
- **Parameters changed, nothing else.** Wall insulation layer, ceiling insulation layer, foundation insulation
  layers (only if dr_2J-09 gives a value), window U and SHGC (`WindowMaterial:SimpleGlazingSystem`), and the
  house's leakage areas (`ZoneLeak_*` effective leakage areas scaled by one factor k; attic and crawl vents left
  unchanged). Geometry, HVAC, schedules, weather and every other object stay byte-identical.
- **How RSI is set.** Change the insulation layer's thickness at fixed conductivity so that the assembly's
  RSI (layers plus EnergyPlus default film resistances, computed and written down) hits the target. If the
  source gives nominal insulation RSI only, set the layer's RSI to it and say so.
- **How air-tightness is set.** From the IDF's own leakage objects compute the house's implied ACH50:
  flow at 50 Pa = Σ over surfaces of Cd × ELA × sqrt(2 × ΔPref / ρ) × (50 / ΔPref)^n with the IDF's Cd, ΔPref and
  n, and ρ = 1.204 kg/m³; ACH50 = flow × 3600 / conditioned volume. Report the current model's ACH50 first. Then
  k = target ACH50 / current ACH50 on every `ZoneLeak_*` ELA (flow is linear in ELA).
- **Values.** Filled only after dr_2J-09 returns and passes the 7-step vetting. Pre-registered rule: use
  MEASURED values first, SURVEY second, never ASSUMED or code values. Regional values for the city's province
  where they exist, otherwise national for all six cities. Several sources for one parameter: the one with the
  largest sample, not an average. If wall, ceiling, window or air-tightness is NOT FOUND after vetting, **WP7.3
  is not run** and the paper states the single current-code envelope as a limitation.
- **Runs.** SingleD × 6 cities × 50 × {2022, 2030} = **600 runs**, `run_paired_mc.py --n 50 --seed 42 --years
  2022,2030 --sched-dir T21/sched_activity`, from a copy of `T22/code/repo` in which only the SingleD IDF(s) are
  replaced by the variant. Output `T31/out/<cell>/`. Same households as T21.
- **Compute.** `-c 4 --mem=16G`, `--array=0-5%2`, `--nice=100`. About 12 CPU-hours.

## Acceptance
Phase A (smoke collector):
- **E0 identity.** The builder run with the model's **current** values writes an IDF whose simulation gives the
  same annual facility kWh and the same annual heating energy as the unmodified IDF for 2 households of
  `SingleD__Montreal_6A`, within 0.001 %. Text diff of the two IDFs: no changed line except comments.
- **E1 the knobs move.** A mechanism-test variant (wall and ceiling RSI halved, window U 2.8, k = 3; labelled
  MECHANISM TEST, never reported) raises annual heating energy for the same 2 households. Report by how much.
- **E2 ACH50.** The current model's implied ACH50 and the arithmetic, written under Verified.
Phase B (collector):
- **E3 completeness and pairing.** 600 runs, 8,760 rows each, `(sample, hh_id)` equal to T21's Step-8 SingleD
  manifests (6/6), no "schedule.json not found" or "invalid" lines.
- **E4 does the gap close (plan WP7 test a).** Stock-weighted SingleD EUI 2022 and 2030 on the Table 5 basis
  (conditioned area, all fuels), next to the T21 current-envelope value and the SHEU band 130.6–186.1 kWh/m².
  Report inside or outside; by end use as T07 did.
- **E5 do the conclusions survive (plan WP7 test b).** SingleD 2022→2030 deltas of midday share, load factor,
  peak hour, mean daily peak kW and annual kWh: same sign as the current envelope, and the ratio of the two
  deltas. A sign change is written in the paper as a limitation, not rerun.

## Phase A brief (employee, Sonnet) — builder and identity smoke; nothing else
Rules: login node = `sbatch squeue sacct scancel scontrol cd ls scp module load` plus single-file
`tail/head/grep/wc -l/cat` only. Never python, `find`, `du`, `md5sum`, `cp`, `mkdir` or blocking `srun` there.
ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`; tcsh, no `2>&1`, no `2>/dev/null`.
Python `/speed-scratch/o_iseri/envs/step4/bin/python`; `ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`. Every
job `-p ps -t 7-00:00:00`. Never write into another task's directory. No edits to repo files or to any original
IDF; local `py -3 -m py_compile` and `bash -n` only. Do not search the literature and do not pick envelope values.
**Submit and end your turn — never wait, never poll.** Write state here as you go.
1. Read T27 Q3, T22 (Decisions: which SingleD IDF each of the 6 cities uses) and T21 (Decisions). Grep the SingleD
   IDF(s) for the construction, material, glazing and `AirflowNetwork` leakage objects and the surfaces that
   reference them. Record every object name and line under Decisions. Compute E2 locally from those numbers
   (small arithmetic, no big files).
2. Write `impl/T31_scripts/make_envelope_variant.py` (inputs: source IDF, a JSON of targets `wall_rsi`,
   `ceiling_rsi`, optional `foundation_rsi`, `window_u`, `window_shgc`, `ach50`; output: variant IDF plus a JSON
   log of every changed field, old and new value). `envelope_current.json` (the model's own values, for E0) and
   `envelope_mechanism_test.json` (E1). `t31_smoke.sh`: builds a tree with the current-values variant and one with
   the mechanism-test variant, runs 2 households of `SingleD__Montreal_6A` year 2022 in each and in an unmodified
   tree, writes annual facility and heating kWh per run to `T31/smoke/e0_e1.csv`. `t31_array.sh` for phase B
   (task 0–5 → SingleD × the six cities), not submitted.
3. Check locally that the builder with `envelope_current.json` gives a text-identical IDF except comments.
4. `scp -r` to `/speed-scratch/o_iseri/2J_revision/T31/`, submit `t31_smoke.sh` only (`-c 4 --mem=16G`, against the
   T22 staged 2022 file). Ledger: JobID, Status SUBMITTED (phase A). End turn.

## Phase B (fresh employee, only after manager go)
Go: E0–E2 collected PASS; dr_2J-09 returned and vetted; manager writes `envelope_existing_stock.json` with each
value's source row under Decisions; T20 N0–N2 and T21 smoke collected PASS. Then build, stage, submit
`t31_array.sh`, JobID to Ledger, end turn.

## Ledger
- **Step 1 (reading + IDF grep).** Read T27 Q3 (envelope facts), T22 Decisions (24-cell list, IDF/EPW
  filenames, T22/code/repo layout), T21 Ledger/Decisions/Verified (exact `run_paired_mc.py` command,
  `--sched-dir` semantics, T21's own smoke pattern used as the template here). Grepped and read line
  ranges of the real SingleD IDF, `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/
  DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` (5,564 lines; only targeted `grep -n` + line-range
  `Read` used, never a full read). No jobs submitted this step.
- **Step 2 (write builder + configs + scripts).** Wrote `impl/T31_scripts/make_envelope_variant.py`,
  `envelope_current.json`, `envelope_mechanism_test.json`, `t31_smoke.sh`, `t31_array.sh` (phase B, not
  submitted), `t31_summarize_smoke.py` (E0/E1 CSV + verdict summarizer, called by `t31_smoke.sh`). Local
  `py -3 -m py_compile` on all three `.py` files -> clean; `bash -n` on both `.sh` files -> clean.
- **Step 3 (local E0/E1 check, required before staging).** Ran the builder locally (`py -3`) against the
  real SingleD IDF with both JSONs. `diff` of the source IDF vs the `envelope_current.json` output: **zero
  lines differ (E0 confirmed locally)**. `diff` vs the `envelope_mechanism_test.json` output: exactly 8
  lines differ (wall insulation thickness, roof/ceiling insulation thickness, window U-Factor, 5x
  `ZoneLeak_*` Effective Leakage Area) -- `wc -l` confirms all three files are 5,564 lines (no line lost
  or merged). **Found and fixed a real bug during this check**: the first version of
  `set_numeric_value()` dropped the line's trailing newline when rewriting a changed field (its regex's
  `rest` group excludes `\n` since `.` does not match newline), which merged two IDF lines into one on
  every changed field. Fixed by explicitly detecting and re-appending the original line ending
  (`\n`/`\r\n`); re-ran the local check after the fix and confirmed clean single-line diffs with matching
  line counts (see `make_envelope_variant.py`'s `set_numeric_value()` docstring/comment for the fix
  in place).
- **Step 4 (stage + submit).** `T31/` did not exist on Speed yet (`ls /speed-scratch/o_iseri/2J_revision/`
  confirmed no `T31` entry) -- `scp -r` cannot create two missing nested directory levels
  (`T31/T31_scripts/`) in one call when the immediate parent (`T31/`) is also missing, so a local
  scratch dir `T31/T31_scripts/<all files>` was built first and `scp -r`'d as one unit to
  `/speed-scratch/o_iseri/2J_revision/T31` (parent `2J_revision/` already existed) -- this created
  `T31/T31_scripts/` in a single `scp -r`, per the hard rule ("create remote directories only by `scp -r`
  of a local folder"). Remote `ls -la` confirmed all files landed byte-for-byte matching the local
  listing.
  - **FINDING, found live on Speed before submitting (see also Decisions/WHAT I DID NOT VERIFY):**
    `ls /speed-scratch/o_iseri/2J_revision/T22/code/repo/2J_docs_occ_nTemp/Step8_docs/` showed only
    `0_BEM_Setup`, `__pycache__`, `eSim_bem_utils_2J`, `run_bem.py` -- **`run_paired_mc.py` itself was
    never staged there**, even though T22's own doc (Ledger Step 2) explicitly lists what it copied
    ("`run_bem.py`, `eSim_bem_utils_2J/*.py`") and does not mention `run_paired_mc.py`, and T21's own
    `t21_smoke.sh`/`t21_array.sh` assume it is there and call it at that exact path. `run_paired_mc.py`
    only imports `eSim_bem_utils_2J.main` and `run_bem` (both already staged, `run_paired_mc.py:25-27`)
    -- no other new dependency. Fixed on the T31 side only (never touched T22/): staged one extra file,
    `T31_scripts/run_paired_mc.py` (unmodified copy of the local `Step8_docs/run_paired_mc.py`), and
    rewrote `t31_smoke.sh` so ALL THREE smoke trees (`unmodified`, `current`, `mechanism_test`) are their
    own `cp -r` copies of `T22/code/repo` (made inside the sbatch job, never on the login node) with this
    one file copied in -- T22/code/repo is now only ever read, never run against directly, and never
    written to.
  - `T17/code/sched/BEM_Schedules_2022.csv` + `_2030.csv` confirmed present via `ls` (used read-only as
    `--sched-dir`, per T22's own proven-working choice -- this smoke does NOT depend on T21's
    currently-blocked T18/T20 chain).
  - **JobID 1328400** -- `sbatch t31_smoke.sh` (`-c 4 --mem=16G -t 7-00:00:00 -p ps`, run from
    `/speed-scratch/o_iseri/2J_revision/T31/T31_scripts/`). Immediate post-submit `squeue -j 1328400`:
    state `R` (running immediately, node `magic-node-10`) -- not waited on further, per the no-parking
    rule.

## Verified
- **E2, computed locally from the IDF's own AirflowNetwork objects (no cluster job needed for this
  number).** SingleD's leakage objects (`...v242.idf:3513-3560`): `ZoneLeak_LongWall` ELA 0.002361197 m²
  (on 4 surfaces: `Wall_ldf_1.unit1`, `Wall_ldb_1.unit1`, `Wall_ldf_2.unit1`, `Wall_ldb_2.unit1`),
  `ZoneLeak_ShortWall` 0.001770898 m² (4 surfaces), `ZoneLeak_Ceiling` 0.00829125 m² (1 surface,
  `ceiling_unit1`), `ZoneLeak_Floor` 8.333e-06 m² (1 surface, `Floor_unit1`), `ZoneLeak_NonGarageWall`
  0.001174867 m² (1 surface, `Wall_ldb_1.garage1`) -- all Cd=1.15, ΔPref=4 Pa, n=0.65. Also present but
  **excluded from "the house's leakage" by design** (Design section: "attic and crawl vents left
  unchanged"): `AtticVent` and `CrawlVent`, 0.37 m² each (4 surfaces each -- the 4 roof-deck surfaces and
  the 4 above-grade foundation-wall surfaces), same Cd/ΔPref/n. Conditioned zone `living_unit1` volume =
  572.2413636775791 m³ (`unheatedbsmt_unit1` 235.63 m³ and `attic_unit1` 83.17 m³ are NOT conditioned).
  Formula per Design section, ρ=1.204 kg/m³: flow(50 Pa) = Cd × ΣELA × sqrt(2×ΔPref/ρ) × (50/ΔPref)^n;
  ACH50 = flow×3600/Vcond. **Using only the 5 `ZoneLeak_*` objects (the house's own conditioned-envelope
  boundary) -> flow = 0.398054 m³/s -> ACH50 = 2.504177** -- a physically plausible, tight, code-built
  house. (Alternative, computed for transparency and REJECTED as the reported number: including
  `AtticVent`+`CrawlVent` in the sum gives flow=45.71 m³/s -> ACH50=287.6, which is not a meaningful
  "house airtightness" number -- these two vent the unconditioned attic/crawl to outdoors and are not
  part of the pressure boundary a blower-door ACH50 test would measure; see Decisions.) Local `py -3`
  arithmetic script output (this session): `ACH50 (house/ZoneLeak_* only) = 2.5041766939807744`.
- **Wall/ceiling assembly RSI, current model (arithmetic only, film-resistance convention documented under
  Decisions, not a chosen envelope value).** Wall (`NBC936_Z6_Wall` = 1IN Stucco + 8IN CONCRETE HW +
  NBC936 Z6 Wall Insulation + 1/2IN Gypsum, films 0.15): current assembly RSI = **4.8086975515292005**
  (insulation layer alone: thickness 0.215 m / conductivity 0.049 W/m-K = RSI 4.388). Ceiling/roof
  (`NBC936_Z6_Roof` = 1/2IN Gypsum + NBC936 Z6 Roof Insulation, films 0.14; this ONE construction is used
  by BOTH the flat ceiling surface `ceiling_unit1` AND the 4 sloped roof-deck surfaces -- the model's own
  choice, not invented here): current assembly RSI = **8.709170918367347** (insulation layer alone:
  0.416 m / 0.049 = RSI 8.490).
- **Local builder test (Step 3 above).** `fields_changed=0` for `envelope_current.json` (E0);
  `fields_changed=8` for `envelope_mechanism_test.json` (E1) -- 1 wall thickness, 1 roof/ceiling
  thickness, 1 window U-Factor, 5 `ZoneLeak_*` ELA values. Printed action log matches the hand-derived
  RSI/ACH50 numbers above exactly (script and hand arithmetic cross-checked, not just one source trusted).

## Decisions
- **FINDING: the window construction the model actually uses is NOT the one named for this variant.**
  The IDF defines `WindowMaterial:SimpleGlazingSystem` "NBC936 Z6 Window Glass" (U=1.6 W/m²-K, SHGC=0.4,
  `:2074-2077`) and a matching `Construction, NBC936_Z6_Window` (`:2290-2292`), but grepping every
  `Window,`/`Door,` object in the file (`:2760-2860`) shows **every real Window object uses construction
  "Exterior Window"**, whose one layer is material **"Glass"** (`WindowMaterial:SimpleGlazingSystem,
  Glass, U-Factor 1.590008, SHGC 0.3344, VT 0.88`, `:2068-2072`) -- `NBC936_Z6_Window` /
  "NBC936 Z6 Window Glass" is defined but never referenced by any surface; it is an orphaned object.
  `make_envelope_variant.py` therefore always edits "Glass" for `window_u`/`window_shgc`, never the
  orphan, and the model's CURRENT window values are **U=1.590008, SHGC=0.3344**, not 1.6/0.4 as a naive
  read of the material list would suggest (T27 Q3 read the material objects but did not check which
  construction real Window surfaces reference -- this is not a criticism of T27, whose brief was reading
  material values, not surface wiring). Not "fixed" (out of scope; a model choice, not a bug this task
  may touch).
- **ACH50 formula scope: `ZoneLeak_*` only, `AtticVent`/`CrawlVent` excluded from BOTH the reported E2
  number and the k-scaling** (matches the Design section's explicit "attic and crawl vents left
  unchanged", extended here to the arithmetic too, not just the scaling). Reasoning: `AtticVent`
  (0.37 m², on the 4 exterior roof-deck surfaces, `attic_unit1`-side) and `CrawlVent` (0.37 m², on the 4
  above-grade foundation-wall surfaces bounding `unheatedbsmt_unit1`) are, by name and placement,
  deliberate vents that connect the UNCONDITIONED attic/crawl zones to outdoors -- not leakage of the
  conditioned envelope. Including them inflates ACH50 by ~115x (2.5 -> 287.6), which is not a
  blower-door-comparable "house airtightness" number and would make the model's current value
  incomparable to any measured/survey ACH50 in dr_2J-09. `ZoneLeak_Ceiling` and `ZoneLeak_Floor` (the
  living-to-attic and living-to-basement boundary leaks) plus the 4 exterior wall leak objects ARE the
  conditioned envelope's own boundary and are what a blower-door test would be measuring. Flagged for the
  manager to confirm before Phase B values are set in stone.
- **Film-resistance convention for assembly-RSI arithmetic (wall 0.15 = 0.12 interior vertical + 0.03
  exterior; ceiling/roof 0.14 = 0.11 interior heat-flow-up + 0.03 exterior/attic-side; foundation 0.0, no
  film applied -- ground-coupled surfaces have no standard air-film convention the same way).** These are
  generic ASHRAE-Fundamentals "still air + standard wind" physics constants used ONLY for the bookkeeping
  arithmetic the Design section calls for ("assembly RSI... plus EnergyPlus default film resistances,
  computed and written down") -- NOT a literature search and NOT an envelope value pick (the hard rule
  bars picking wall/ceiling/window/air-tightness VALUES, not universal film-coefficient constants).
  Flagged because the task doc did not specify an exact convention; the manager may want a different one
  before Phase B locks in real RSI targets from `dr_2J-09` (a different film choice shifts the *reported*
  assembly-RSI number for a given insulation thickness, though it does NOT change what Phase B actually
  needs, since Phase B receives a TARGET assembly RSI and solves backward for thickness regardless of
  which film convention was used to describe the CURRENT model).
- **Builder semantics: null/absent = untouched, not "recompute and hope it round-trips".** Originally
  considered making `envelope_current.json` carry the literal current RSI/U/ACH50 numbers and having the
  builder skip a field only if the recomputed target equals the current value; rejected because
  floating-point round-trip through the RSI algebra could differ from the original by ~1e-15 and change
  the IDF's text (`repr()` prints full precision), breaking the "no changed line except comments"
  requirement by construction. Instead, every JSON key defaults to `null` = "do not touch this field at
  all" (checked directly, before any arithmetic), so `envelope_current.json` (all keys null) is
  guaranteed byte-identical with zero risk, and is not merely "believed" identical -- confirmed by local
  `diff` (Step 3).
- **T22's staged repo is missing `run_paired_mc.py`** (see Ledger Step 4 FINDING). Not fixed inside
  T22/ (out of scope, read-only). Fixed on the T31 side by staging our own copy and copying it into every
  T31-local tree this script builds. **This also affects T21**: T21's own `t21_smoke.sh`/`t21_array.sh`
  call `$CODE_ROOT/2J_docs_occ_nTemp/Step8_docs/run_paired_mc.py` with `CODE_ROOT=T22/code/repo` directly
  (no local copy step) -- when T21's queued jobs (1328378/1328380, currently `PD (Dependency)`) finally
  run, they will hit "file not found" on the driver itself, a DIFFERENT and earlier failure than the
  T18/T20 upstream block T21's own doc already flagged. Recorded here for the manager/collector; not
  fixed in T21's directory (out of scope, "never write into another task's directory").
- **Mechanism-test JSON values are literal, hand-derived-then-cross-checked numbers, not a formula
  evaluated at runtime**: `wall_rsi=2.4043487757646003` and `ceiling_rsi=4.3545854591836735` are exactly
  half of the current assembly RSIs above (Design section: "wall and ceiling RSI halved"), `window_u=2.8`
  and `k=3` are the literal values the Design section names. Computed once locally (Python), then
  independently reproduced by the builder's own printed "current_assembly_rsi" (Verified) -- both agree.
- **Driver-path fix (2026-09-15, T21 employee, cross-task pointer): T31's scripts were NOT edited.**
  `t31_array.sh` has no hardcoded `T22/code/repo` path (only a comment; the real path is the required
  env var `VARIANT_CODE_ROOT`, Phase B, not submitted). `t31_smoke.sh`'s `T22_CODE_ROOT` (line 66) is
  only a `cp -r` source inside `build_tree()`, immediately overwritten with this task's own staged
  `run_paired_mc.py` before the driver is ever called at that path (lines 96-104) -- it does not break,
  so per the manager's live direction it was left unchanged. Job **1328400 confirmed still RUNNING**,
  zero "No such file" lines in its log at check time -- left alone. Full reasoning in
  `2026-09-15_T21_wp1_step8_step9_rerun.md`, "Ledger (2026-09-15, driver path fix)".

## Next
Phase A employee: DONE -- builder + configs + smoke/array scripts written, local E0/E1 identity checks
passed, staged to `/speed-scratch/o_iseri/2J_revision/T31/`, smoke job **1328400** submitted (`R`
immediately after submit; not waited on further). Collector (fresh agent, later): `sacct -j 1328400` for
exit code; if COMPLETED, `scp` back `T31/logs/t31_smoke_1328400.out` and `T31/smoke/e0_e1.csv`, confirm
the job's own printed `[E0]`/`[E1]` verdict lines say PASS, and paste E0/E1/E2 results into the task doc's
top-level Acceptance section. Manager: (1) confirm the window-material FINDING and the
`ZoneLeak_*`-only ACH50 scope decision above before Phase B; (2) note the T21 `run_paired_mc.py`
missing-file finding for whoever collects/reruns T21; (3) author: run `dr_2J-09` when convenient (Phase B
values still needed).

## WHAT I DID NOT VERIFY
- Did not wait for or poll job 1328400 beyond the one immediate post-submit `squeue` (state `R`); no
  evidence yet that any of the three legs (`unmodified`/`current`/`mechanism_test`) actually completes an
  E+ run, that `run_paired_mc.py` behaves identically once copied out of its usual location, or that the
  `[E0]`/`[E1]` verdicts in `t31_summarize_smoke.py`'s own printed output say PASS on real E+ output
  (only checked E0 as a pure text-diff locally, before any simulation).
- Local E0/E1 checks (Step 3) verified the builder's TEXT-LEVEL output only (diff, line counts, printed
  action log) -- did not run EnergyPlus locally (no local E+ install used this session) to confirm the
  mechanism-test variant's predicted heating-energy INCREASE actually materializes in a real simulation;
  that is exactly what job 1328400 is for.
- Did not verify the film-resistance convention (wall 0.15, ceiling 0.14) against any specific ASHRAE
  Fundamentals table edition or NBC 936 clause -- used commonly-cited round numbers from general
  engineering knowledge, flagged explicitly in Decisions as a convention needing manager sign-off, not
  presented as an authoritative sourced value.
- Did not check whether `NBC936_Z6_BasementWall`'s and `NBC936_Z6_SlabOnGrade`'s OTHER-layer materials
  (`HW CONCRETE`, `CP02 CARPET PAD`) are used ONLY there or also shared with other constructions the way
  `NBC936_Z6_Roof` turned out to be shared between ceiling and roof-deck surfaces -- foundation is
  optional and untouched in both Phase A JSONs, so this was not load-bearing for E0/E1, but Phase B
  (if `dr_2J-09` returns a foundation value) should re-check this before trusting `apply_assembly_rsi_target`
  for the foundation case.
- Did not check disk usage/quota under `/speed-scratch/o_iseri/2J_revision/T31/` before submitting --
  three `cp -r` copies of T22's staged repo (16 .py files + 4 IDFs + 6 EPWs each) will use noticeably more
  space than the single-tree smokes T19/T21 ran; not sized in advance (same gap every prior task in this
  series has recorded).
- Did not independently re-verify that `AttachedHouse`/apartment IDFs follow the same
  `ZoneLeak_*`/`AtticVent`/`CrawlVent` naming pattern -- this task is SingleD-only per the Design section,
  so only the one IDF (`DetachedHouse+...v242.idf`) was read.

## Collector (2026-09-15, smoke)
Job 1328400: `sacct -j 1328400` -> `t31_smoke` COMPLETED, ExitCode 0:0, Elapsed 00:07:50. Batch step
MaxRSS 1141212K (~1.09 GB); extern step MaxRSS 256K. Well inside the 16G request. Remote log
`/speed-scratch/o_iseri/2J_revision/T31/logs/t31_smoke_1328400.out` (229 lines, only one log file --
no separate `.err` file exists under `T31/logs/`, confirmed by `ls`). `T31/smoke/e0_e1.csv` (6 rows)
and the job's own printed `[E0]`/`[E1]` lines were both read; ACH50 and the window-material chain were
re-derived independently from the local IDF, not just re-read from the doc's Verified section.

| check | values | source | pass line | verdict |
|---|---|---|---|---|
| E0 identity, hh 130168 | facility 8168.869539 vs 8168.869539 kWh; heating 5577.298212 vs 5577.298212 kWh; diff 0.000000% both | `e0_e1.csv` rows 1/3; log:225 | within 0.001% | PASS |
| E0 identity, hh 79150 | facility 8118.736606 vs 8118.736606 kWh; heating 5605.157678 vs 5605.157678 kWh; diff 0.000000% both | `e0_e1.csv` rows 2/4; log:226 | within 0.001% | PASS |
| E0 same households both trees | unmodified and current both drew sample 1 = hh 130168, sample 2 = hh 79150 | `e0_e1.csv` | same 2 IDs in both trees | VALID (comparison is like-for-like) |
| E0 IDF text-diff | byte-identical, comments included | log:146-147 | zero changed lines except comments | PASS |
| E1 knobs move, hh 130168 | heating 5577.298212 -> 17164.889366 kWh, +11587.591154 kWh (+207.76%) | log:227 | heating rises | PASS |
| E1 knobs move, hh 79150 | heating 5605.157678 -> 17072.377409 kWh, +11467.219731 kWh (+204.58%) | log:228 | heating rises | PASS |
| E2 ACH50 arithmetic | ELA counted once per surface reference (not once per named leak component): 4x`ZoneLeak_LongWall` 0.002361197 + 4x`ZoneLeak_ShortWall` 0.001770898 + 1x`ZoneLeak_Ceiling` 0.00829125 + 1x`ZoneLeak_Floor` 8.333e-06 + 1x`ZoneLeak_NonGarageWall` 0.001174867 = 0.02600283 m2; Cd 1.15, dPref 4 Pa, n 0.65 (idf:3514-3560, all 5 objects grepped and match exactly); Vcond 572.2413636776 m3 (idf:2313, Zone `living_unit1`, matches exactly) -> flow 0.3980537 m3/s -> ACH50 2.5041767 | recomputed independently with `py -3`, local IDF `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/DetachedHouse+CZ6A+IECC+2024_NBC936_Z6_v242.idf` | reproduces doc's 2.504177 to 6 decimals | CONFIRMED (doc's number and formula are correct; the one thing the doc's Verified text does not spell out is that the per-component ELA must be multiplied by how many surfaces reference it -- 4 for the two wall components -- otherwise the answer comes out 1.310, not 2.504) |
| E2 window material | idf:2760-2840, all 8 `Window,` objects reference Construction "Exterior Window" (idf:2202-2204), whose one layer is material "Glass" (idf:2068-2072): U-Factor 1.590008, SHGC 0.3344 | grepped directly | matches doc's "U 1.59, SHGC 0.33" | CONFIRMED |
| log errors | grep -in for invalid / not found / Traceback / Error / No such file | `t31_smoke_1328400.out` | 0 matches | PASS (0 matches, no examples) |

What would have failed E1: heating energy falling or staying flat for either household under the
mechanism-test knobs (halved wall/ceiling RSI, window U 2.8, leakage x3) would have meant the builder's
edits are not reaching the simulation.

Status: **SMOKE PASS.** All of E0 (identity, valid same-household comparison), E1 (heating rises,
+204.6% and +207.8%), and E2 (ACH50 arithmetic and window material both reproduce independently) are
confirmed against the real completed job, not just the local pre-run text checks. Phase A is closed.

Next: manager go for Phase B, once `dr_2J-09` returns and is vetted (envelope values still needed;
nothing else owed by this collector task).

WHAT I DID NOT VERIFY (smoke collector)
- Did not re-run or spot-check any of the 8760 hourly rows behind the annual kWh totals in `e0_e1.csv`
  -- only the annual sums (facility, heating) were compared, per the task's E0/E1 acceptance wording.
- Did not investigate the "Dropped 93 households (failed schedule sanity check)" line that appears once
  per tree build (log:14, 86, 163) -- not one of the required error keywords, and overall job verdict
  was `FAIL=0`, so left unflagged.
- Did not confirm whether stderr is merged into the single `.out` file or simply never produced --
  `ls T31/logs/` shows only `t31_smoke_1328400.out`, no `.err` file of any name.
- Did not check Speed disk usage/quota for the three `cp -r` trees this job built (same gap the phase A
  employee already recorded, still open).
- Did not verify facility_kWh's small E1 decrease (~0.3-0.5%, both households) -- not a pass/fail
  criterion in the Acceptance section, so not investigated further.

## Manager addendum (2026-09-15, after phase A)
- Phase A accepted. E0 local text identity and E1 eight changed fields noted; E0-E2 verdicts still come from the
  smoke collector (job 1328400).
- Window: the model's glazing is the material actually referenced by the SingleD window constructions ("Glass",
  U 1.59, SHGC 0.33), not the unused "NBC936 Z6 Window Glass". Accepted, because the reference chain from the
  window surfaces was traced. The collector confirms it by grep of the construction the fenestration surfaces use.
- ACH50 scope: only `ZoneLeak_*` objects (house envelope), current model **2.50 ACH50**; attic and crawl vents are
  excluded, because a blower-door test measures the conditioned volume with the attic outside it. Accepted. The
  scaling factor k applies to `ZoneLeak_*` only, as the Design says.
- Driver path: T31 staged its own unmodified `run_paired_mc.py` copy; the shared-tree fix (T21 Ledger) may re-point
  `t31_smoke.sh`/`t31_array.sh`. Whichever is used, E0 must still compare like with like.

## Manager addendum (2026-09-15, after smoke collector)
- E0 PASS (0.000000 %, same households, IDFs byte-identical), E1 PASS (heating +208 % and +205 %, mechanism test
  only, never reported), E2 PASS (2.5042 ACH50 re-derived; ELA counted once per surface that references a leakage
  component, which is how AirflowNetwork applies it; k scales the component, so flow stays linear in k). Window
  "Glass" confirmed through the construction chain. Phase A CLOSED.
- The smoke ran 2022 only and drew 130168/79150 (the 2022-only pool). Phase B runs 2022,2030 through the paired
  driver, so it inherits the T21 sample question (log (ai)); phase B also waits on that answer, besides dr_2J-09.

## Manager note (2026-09-15, after T21 diagnosis 1328414)
- The smoke's `130168, 79150` draw came from the published schedules (`T17/code/sched/`), not the Nb-f stock; E0-E2
  are mechanics checks and stand. Phase B runs `run_paired_mc.py` on `T21/sched_activity` (paired pool), so its
  sample equals T21's by construction (SingleD__Montreal_6A: `130228, 79252`). The T21 sample question is CLOSED
  for T31. The only remaining gate for phase B is dr_2J-09 returned, vetted, and `envelope_existing_stock.json`
  written by the manager.

## Manager vetting of dr_2J-09 (2026-09-15, plan log (ap))
Return: `deepResearch/dr_2J-09_existing_stock_envelope_results.md` (187 lines, 121 value rows, verdict USABLE).
README vetting steps: (1) positive control present, reported resolved; (2) DOIs and (3) source opening are
moved into a verification pass, because the assistant does not open literature (CLAUDE.md); (4) applied
below; (5), (6) not applicable; (7) offline audit done, verification pass written:
`deepResearch/dr_2J-09b_envelope_verification_prompt.md` (author runs it).

Offline audit findings (no web page opened):
- **A. Rows the scout computed.** 53 rows credited to the CanmetENERGY archetype CSV. Except the Slide 20 rows,
  they are unweighted means and medians over archetypes computed by the scout (its own log shows the pandas
  calls). The prompt forbade averaging; an archetype mean is not a stock mean; "5,023 SD" counts archetypes;
  "2000-2019" is shown nowhere. **Rejected.** The two "Calculated from Tables 5.9 and 7.2" window rows: **rejected**.
- **B. Sample sizes.** Swan Table 3.4 regional n sum to 15,000, not the 14,030 single-detached total; every
  vintage row carries the total. Regional n are unverified.
- **C. Summary-only numbers** (wall 1.95 / 2.81, ceiling 3.39 / 5.13, ACH50 6.95 / 6.24 / 4.64 / 3.78) appear
  in no table row. Not used.
- **D. Never opened.** Khemet and Richman (2018): only Crossref metadata fetched, yet "5.7 ACH50, p. 91",
  "72 %", "~900,000" given. Hamlin and Gusdorf (1997): no retrieval visible. SHEU-2019 window mix: fetch
  returned no table. All three **held** until the verification pass.
- **E. Labels.** The scout says the Swan window U/SHGC are Window 5.2 ratings (centre-of-glass or assembly),
  labelled MEASURED. Wall/ceiling "effective" vs nominal not quoted. Glazing share basis (area or count) not
  quoted.
- Only Swan (2010) was actually downloaded and read by the scout (pages visible in its log).

Value-selection rule for `envelope_existing_stock.json`, fixed now, before the verification pass returns
(applies T31 Design "Values"; interpretations recorded here so they cannot move after the numbers are seen):
1. Only rows marked CONFIRMED or CORRECTED (printed value) in dr_2J-09b are eligible. Scout-computed rows never.
2. **Geography first, then sample size.** For each city use a value published for its province; where the
   source publishes only a region containing the province (Swan's "Prairies" for Calgary and Winnipeg), that
   region counts as the province, stated in the paper. Among eligible sources at that level, the largest
   sample of houses. If no eligible value exists at that level for a city, national values for all six cities.
3. **Stock average across all vintages**, not a vintage row (the model has one SingleD envelope per city).
4. Wall, ceiling, foundation: set as effective assembly RSI if the source says effective; as insulation-layer
   RSI if it says nominal (T31 Design "How RSI is set"); NOT STATED is treated as effective and stated.
5. **Window: the dominant glazing type's printed U and SHGC** (never a mix average). If the printed values are
   centre-of-glass only, use them and state as a limitation that frames are not represented, which understates
   window loss (conservative for gap closing). No printed U or SHGC for the dominant type = window NOT FOUND.
6. ACH50 sets k = target / 2.5042 on every `ZoneLeak_*` ELA.
7. Collection years 1997 to 2006 are accepted. Stated in the paper: homes retrofitted since then make the 2022
   stock tighter and better insulated than these audits, so the variant brackets the gap from the leaky side.
8. If wall, ceiling, window or ACH50 ends NOT FOUND after dr_2J-09b: WP7.3 not run; one-envelope limitation.

Status: phase B gate = dr_2J-09b returned + manager applies rules 1 to 8 and writes the JSON with each value's
source row here. T21 Step 8 must also have finished (same households).

## Manager application of rules 1 to 8 to dr_2J-09b (2026-09-15, plan log (aq))
Return: `deepResearch/dr_2J-09b_envelope_verification_results.md` (366 lines; author ran it; survival count
as returned 27 CONFIRMED / 6 CORRECTED / 6 NOT FOUND).

Audit of the return (offline, no page opened by the manager):
- Positive control (Swan and Ugursal 2009) resolved: method not broken.
- Swan (2010) PDF was downloaded and read (tool log shows page extraction of PDF p. 99, 172-173, 242): Table 3.4
  rows usable as copied. Answers: effective/nominal NOT STATED; means; single-detached only; no sample size
  printed (the 15,000 are Table 3.2 targets); audits 1997 to 2006.
- Khemet and Richman (2018): the paper was NOT opened (paywall, stated by the tool); values come from Khemet's
  2019 thesis Chapter 4. Page numbers given for the paper are therefore unverified; only thesis pages count.
- Hamlin and Gusdorf (1997): marked CORRECTED, but the tool states it could not download either PDF. Treated
  as **NOT FOUND** (never opened). Not load-bearing.
- SHEU-2019 window table: dwelling counts printed; the percentages are the tool's own arithmetic. Not load-bearing.

Rules applied:
- Wall RSI (rule 1-4): eligible, Swan Table 3.4 regional means, NOT STATED = effective. **FOUND.**
- Ceiling RSI: eligible, Swan Table 3.4 regional means. **FOUND.**
- ACH50: eligible (Swan regional; Khemet thesis Table 4 provincial arithmetic means with larger samples). **FOUND.**
- Window (rule 5): dominant glazing type = Swan code 200, double glazed clear 13 mm air, 74.0 % of
  single-detached window area (Table 7.2). Its U-value and SHGC are **NOT PRINTED** in Tables 5.9, 5.10 or 7.2;
  no other eligible row prints a window U or SHGC (CanmetENERGY: NONE PUBLISHED). **Window NOT FOUND.**
- **Rule 8 fires: WP7.3 is not run.** `envelope_existing_stock.json` is not written. T31 phase B is closed
  without runs. The paper states the one-envelope limitation: every building type uses one current-code
  envelope, so heating energy is not calibrated and the energy-intensity gap by end use (WP7 step 2) is where the
  envelope effect is discussed. No partial variant (walls, ceiling and air-tightness only) is run: rule 8 was
  fixed before the numbers were seen, and a partial variant would be a new design, not this one.

Status: **T31 CLOSED, not run (rule 8, window NOT FOUND).** Phase A results (mechanics) stay in this doc only.
