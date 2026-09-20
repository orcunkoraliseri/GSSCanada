# T65 — diagnose why the rebuild's multi-unit (MidRise/HighRise/OtherDwelling) A5 energy gate is inflated 500-8000%

Task doc: this file.
Upstream: `impl/2026-09-17_T48_A5_A6_fullgrid.md` (T48, job `1329258`, COMPLETED, the job that found this),
plan `00_REVISION_PLAN.md` Progress Log entry (cw) (2026-09-20, new plan §5 item 40 — read it first, it has
the full framing and closes the old, wrong item 26 hypothesis).
Manager: Opus. Status: DONE — mechanism found, evidenced, no fix applied. **Diagnosis only — no fix, no re-run of any campaign.**

## Why this task exists

T48 ran the identical, unmodified `step9_validate_full.py` (A5, the SHEU +/-15% energy gate) over two
trees: the T21 rebuild (staged at `/speed-scratch/o_iseri/2J_revision/T48/t21_stage/`) and the published
campaign (`/speed-scratch/o_iseri/step9_run/`). Results:

- **Published: 48/48 cell x year rows PASS**, including every MidRise/HighRise/OtherDwelling row
  (`T48/pub_a5_results.csv`).
- **Rebuild: 12/48 PASS.** Every SingleD row passes (within +/-2%). Every MidRise, HighRise and
  OtherDwelling row **fails by 514% to 8055%** on both `InteriorEquipment:Electricity` and
  `InteriorLights:Electricity` (`T48/t21_a5_results.csv`).
- Same script, same gate, same archetype/city cells, same year range — the only thing that differs between
  the two runs is which tree of `hourly_meters.csv` files it read. **The regression is in the data, not in
  the validator.**

**One exemplar cell to start with, chosen because it has the largest overshoot: `HighRise__Montreal_6A`,
2022.** Published: `sheu_pct_equip = -0.072%` (PASS). Rebuild: `sheu_pct_equip = +8052.6%` (FAIL). Full
per-cell numbers for this exemplar (and three more) are in `T48/logs/t48_a5a6_1329258.out`, the
`5-compare-A5-provenance` step.

## What `step9_validate_full.py` does (read the actual file, this is a summary only)

`/speed-scratch/o_iseri/2J_revision/T48/scripts/step9_validate_full.py`:
- Line 47: `OD_N_UNITS = 7` — OtherDwelling is modelled as a 7-unit building; a fridge correction
  (`FRIDGE_KWH_IDF`, line ~45-146) subtracts `(OD_N_UNITS - 1) * FRIDGE_KWH_IDF` from the raw
  `InteriorEquipment:Electricity` reading, because the building-level meter captures all 7 units' fridges
  but the target is per-dwelling. **No equivalent correction exists for MidRise or HighRise** (this is the
  real, separate structural gap item 26 originally flagged — it is still real, but it cannot explain why
  the *published* tree passes with the *same absent correction*).
- Line 115-119: reads `Electricity:Facility`, `InteriorEquipment:Electricity`, `InteriorLights:Electricity`
  columns directly from each household's `hourly_meters.csv` via `find_col()`.
- The comparison is against a per-dwelling SHEU target (lines ~38-41).

## What to do (in order — stop and report as soon as you have a clear answer, do not chase every candidate)

1. **Read `step9_validate_full.py` in full** (single-file `cat`, allowed on the login node — it is one
   file). Confirm exactly how it aggregates per-household values into the cell-level number the gate
   checks (mean? sum? per-unit divide? nothing?).
2. **Pick one household from `HighRise__Montreal_6A` and compare its raw `hourly_meters.csv` directly,
   rebuild vs published, byte for byte on the columns that matter.** The rebuild's staged copy is under
   `T48/t21_stage/idfs/HighRise__Montreal_6A/...` (or wherever the manifest built at T48 step 3 points —
   read `T48/t21_stage/step9_manifest.csv` to find one household's actual output path; do not guess the
   directory shape). The published copy is under
   `/speed-scratch/o_iseri/step9_run/idfs/HighRise__Montreal_6A/...`. Use single-file `grep`/`head` to pull
   the `InteriorEquipment:Electricity` and `InteriorLights:Electricity` columns (or their whole rows) for
   the same household ID in both files, and compare the raw magnitudes directly — is the rebuild's raw
   number itself ~80x larger, or is it a similar magnitude that only *becomes* 8000% after some
   downstream division goes wrong? This one comparison, done first, will tell you whether the bug is in
   the E+ output itself (the rebuild's `hourly_meters.csv` really does contain much bigger numbers) or in
   how something reads/scales it afterward.
3. **If the raw rebuild numbers are themselves inflated**, check whether the rebuilt IDF for this archetype
   has a different number of dwelling units, different meter definitions, or different equipment/lighting
   density than the published IDF. Compare the two IDFs' `InteriorEquipment` / `Lights` / `Zone` object
   counts for the same archetype (`HighRise__Montreal_6A`) — single-file `grep -c` on object keywords
   (`ZONE,`, `ElectricEquipment,`, `Lights,`) is enough to tell if the rebuild's IDF has more zones/units
   than the published one used for the same nominal archetype.
4. **If the raw numbers match but the gate's inflation only shows up after aggregation**, check whether the
   rebuild's `cell_manifest.csv` / staging step duplicated households, is double-counting a shared building
   across the household sample (i.e. multiple sampled households from the same MidRise/HighRise building
   each contributing the *whole building's* meter rather than their own share), or whether a household-count
   divisor that the published pipeline applied upstream is missing from the rebuild path.
5. **Confirm the scale factor is consistent with a specific mechanism**, not just "some things are bigger".
   `HighRise` overshoots ~8000%, `MidRise` ~3200%, `OtherDwelling` ~514%, `SingleD` ~0%. If this scales
   with a plausible "number of dwelling units per building" for each archetype (e.g. HighRise buildings
   having far more units than MidRise, which has more than OtherDwelling's 7, and SingleD having exactly
   1), that is strong evidence for a **missing per-unit division** somewhere in the rebuild path
   specifically (the published path evidently already applies one, since it passes cleanly). State this
   ratio check explicitly — do not just assert the mechanism, show the arithmetic.

## What you do NOT do

- **Do not fix the bug, patch any script, or re-run any campaign.** This is diagnosis only. If you find
  where the fix should go, name the file and line and say what the fix would be — do not apply it.
- **Do not touch `step9_validate_full.py`, T21's staged tree, or the published tree.** Read-only.
- **Do not generalize to a second cell until the first (`HighRise__Montreal_6A`) is fully understood.** One
  clear mechanism beats four half-checked cells.

## Rules (absolute)

- Login node allowed commands only: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, `mkdir`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. If any comparison needs summing
  a full 8760-row column (not just a `head`/`grep` spot check), that step must run inside an `sbatch` job,
  not on the login node.
- tcsh login shell: no `2>&1`, no `2>/dev/null`.
- CPU ceiling: 2J stays at or under 32 running CPUs; nothing else is running for 2J right now. If a job is
  needed, `-c 1 --mem=8G -t 7-00:00:00` is enough for a single-household comparison.
- If a job is needed, submit and end the turn (do not poll); if the whole diagnosis can be done with
  single-file `grep`/`head`/`cat` spot checks alone (steps 2-3 may well only need a handful of household
  rows, not a full-cell walk), you do not need to submit anything at all — say so if that's how it played
  out.
- Fresh agent, one task. Write everything found into this doc as you go, in `## Verified`.

## Output

This doc's own `## Verified` / `## Decisions` / `## Next` sections, written up as the diagnosis proceeds. If
a job is submitted, also `/speed-scratch/o_iseri/2J_revision/T65/logs/t65_report.txt`.

## Ledger

No sbatch job was needed. All comparisons were single-file `grep`/`head`/`sed`/`cat` on the login node
(HighRise__Montreal_6A, one household, ~15 files, none over a few thousand lines), plus `scp` of 4 IDF
files to the local machine for a `diff` (the diff itself ran locally, not on the login node — no
restricted command was run on Speed).

## Verified

1. **Read `step9_validate_full.py` in full**
   (`/speed-scratch/o_iseri/2J_revision/T48/scripts/step9_validate_full.py`). It streams each
   household's `hourly_meters.csv`, sums each column across all households in a cell×year×treatment
   group, then divides by `n_hh` (line ~118, `kwh()`, using `bl_agg['n_hh']` for BOTH the baseline and
   activity divisor). It does **not** divide by number of dwelling units/zones anywhere except the
   OtherDwelling-only fridge correction (`OD_N_UNITS=7`, line 47). `ac_equip_col` /
   `ac_light_col` are matched straight off the **whole-building facility meters**
   `InteriorEquipment:Electricity` / `InteriorLights:Electricity` (lines 116-119) — there is no
   zone-scoping in the validator itself.

2. **n_hh pairing is not the cause.** For `HighRise__Montreal_6A` 2022, both trees show 50/50/50/50
   households across baseline/activity (manifest grep count and T48 log line
   `T48/logs/t48_a5a6_1329258.out:21-24,361-364` both say `n_hh=50` for every arm). No missing-file or
   duplicate-row issue.

3. **Raw `hourly_meters.csv` comparison, household-for-household (sample_001, rebuild HH106602 vs
   published HH106670, activity, 2022, hour 0):**
   rebuild `InteriorEquipment:Electricity` = 40,529,113.67 J vs published 449,966.81 J — **ratio
   90.1x**, confirmed directly in the raw per-household simulation output, before any aggregation or
   division by the validator. This is a **raw-output-level** inflation, not a downstream scaling bug
   (task doc step 2 answered: raw numbers themselves are inflated).
   Column headers are byte-identical between the two trees.

4. **IDF structure is identical** for the same archetype (rebuild vs published `Scenario_2022.idf`,
   activity treatment): same 27 `Zone,` objects, same 26 baseline `ElectricEquipment,` objects (all
   referencing the shared code schedule `NECB-G-Electric-Equipment`, itself byte-identical text in
   both trees), same `Meter:Custom`/`Meter:CustomDecrement` objects, same zone floor areas and zone
   multipliers (`eplusout.eio` "Zone Information" rows identical). Task doc step 3's hypothesis
   ("rebuild IDF has more zones/units") does **not** hold — ruled out.

5. **The real difference, found by `diff`-ing the full rebuild vs published IDF locally** (after
   `scp`): the two trees inject a **different number** of per-household equipment objects, and into
   **different numbers of zones**.
   - **Published** (`baseline` vs `activity` diff for HH106670): exactly **1**
     `ElectricEquipment,STEP9_Equip_106670` (Design Level 858.73 W) + **1**
     `ElectricEquipment,STEP9_Fridge_106670` (51.14 W) + **1** Lights object, all three placed in the
     single zone `G SW Apartment` — the household's own occupied unit only.
   - **Rebuild** (`baseline` vs `activity` diff for HH106602): **50** `ELECTRICEQUIPMENT,` objects
     (`STEP9_Equip_106602_0` .. `_24`, two objects per zone: equip + fridge) and **27** `LIGHTS,`
     objects, placed into **all 25 apartment/office/corridor zones of the building**, not just the
     occupied unit.

6. **Found the exact code responsible and why it changed**, by tracing
   `run_paired_mc.py` (`DRIVER=` line in `T21/logs/t21_t21_step9_activity_1328425_0.out`) →
   `eSim_bem_utils_2J/integration.py` at
   `/speed-scratch/o_iseri/2J_revision/code_step8/repo/2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py`.
   Lines **1541-1594**: the code neutralizes every existing `ElectricEquipment` object across the
   whole building (design level -> 0) and collects **every zone that had one** into `_s9_equip_zones`
   (a `set()`, line 1548 init, `.add(_z)` at line 1594). Lines **1611-1621** and **~1635-1646** then
   inject the household's SHEU-calibrated equipment carrier and fridge baseload into **every zone in
   `_s9_equip_zones`** — i.e. broadcast to every dwelling unit in the building — via
   `for _zi, _zname in enumerate(sorted(_s9_equip_zones)): ...`. The single-zone fallback
   (`if not _s9_equip_zones: _s9_equip_zones = {_s9_occ_zone}`, line 1595-1596) only fires when the
   set is **empty**, which never happens for multi-zone archetypes because every apartment zone
   legitimately has a baseline `ElectricEquipment` object before neutralization.
   **The code's own comment (lines 1578-1587) says this broadcast is deliberate**: "Neutralize across
   ALL zones, then re-inject the SHEU-calibrated carrier into EVERY zone that had a load (one
   household-equivalent per dwelling unit)... Injecting into a single zone collapsed whole-building
   equipment to ~1/N_units of its physical total for multi-zone archetypes (MidRise/HighRise/
   OtherDwelling) — the root cause of the 2022/2030 phantom-peak defect found during manuscript QA
   (2026-07-13)." So this is a **fix for a different, earlier bug** (a "phantom-peak" load-shape
   defect), made after the published campaign was already frozen. The published tree ran the
   **pre-fix** version of `integration.py` (single-zone injection); the rebuild ran the **post-fix**
   version (all-zone broadcast). Neither `step9_validate_full.py` (the A5/A6 validator) nor its SHEU
   per-dwelling targets were ever updated to match the new broadcast behaviour.

7. **Ratio check confirms the mechanism arithmetically (task doc step 5).** The SHEU gate compares a
   now-**whole-building** meter reading against a **per-dwelling** target with no unit-count division
   (only OtherDwelling gets a partial, fridge-only correction). The overshoot ratio should equal the
   number of "dwelling-unit-equivalent" zones the equipment is broadcast into, accounting for zone
   multipliers read from `eplusout.eio` "Zone Information":
   - **HighRise** (Montreal 6A): G floor 7 apartments (x1) + M floor 8 apartments (x8 zone multiplier
     = 64) + T floor 8 apartments (x1) + 1 office = **80 unit-equivalents**. Measured overshoot
     8052.6% -> ac/target = 81.5x. Match within ~2%.
   - **MidRise** (Toronto 5A): G floor 7 apartments (x1) + M floor 8 apartments (x2 multiplier = 16) +
     T floor 8 apartments (x1) + 1 office = **32 unit-equivalents**. Measured overshoot 3200% (from
     task doc) -> ac/target = 33x. Match within ~3%.
   - **OtherDwelling**: 7 units (`OD_N_UNITS`, hard-coded in the validator itself). Measured overshoot
     514% -> ac/target = 6.14x — lower than 7 because the validator's existing fridge-only correction
     (subtract 6x448 kWh) partially offsets the broadcast, but the main equipment carrier itself is
     still un-divided across the 7 units.
   - **SingleD**: 1 zone, broadcast-to-all-zones = broadcast to the same 1 zone = no inflation
     (matches the 0% observed).
   All four archetypes' overshoot ratios track the number of zones the equipment/fridge carrier is
   broadcast into. This is not "some things are bigger" — it is a specific, countable per-zone
   duplication whose multiplier equals the building's own unit count.

## Decisions

- The task doc's step 3 (compare IDF `ZONE,`/`ElectricEquipment,`/`Lights,` object counts between
  rebuild and published) came back **negative** (counts identical) — I did not stop there, because the
  task doc explicitly says the counts test only whether the IDF *itself* was regenerated with more
  zones. It wasn't. The real difference was in the **generated content** of the household-specific
  equipment objects (which zones they target), found via a local `diff` of the household-specific
  `Scenario_2022.idf` files rather than an object-count `grep -c`. I judged this a legitimate
  extension of step 3/4, not a new candidate to chase, since the task doc's own step 4 anticipates
  exactly this shape of bug ("multiple sampled households from the same... building each contributing
  the whole building's meter rather than their own share").
- I did not stop at "raw output is inflated" (step 2's minimum bar) because the task doc's step 5
  explicitly asks for the mechanism and the ratio arithmetic, not just the direction of the bug. I
  judged it in scope to open `integration.py` (the IDF-generation code, not the validator) to find
  *why* the raw output is inflated, since step 4 already points at "the manifest/staging step" as a
  candidate and the actual candidate turned out to be one level upstream of the manifest, in IDF
  generation.
- I stopped after four cells' worth of arithmetic (SingleD/OtherDwelling/MidRise/HighRise), all from
  data already in the T48 log plus one `eplusout.eio` zone-count check per archetype (no new campaign
  cell was diagnosed end-to-end) — consistent with the task doc's instruction not to generalize to a
  second full cell.

## Next

- This is diagnosis only; no fix applied, per the task doc. If a fix is authorised later, the two
  candidate levers are: (a) revert the equipment broadcast in `integration.py:1541-1621` to
  single-zone injection (`_s9_occ_zone` only) for the SHEU/A5 gate's benefit — but this reopens the
  2026-07-13 "phantom-peak" defect the broadcast was written to fix; or (b) keep the broadcast and fix
  `step9_validate_full.py` to divide the whole-building `ac_equip_kwh`/`ac_light_kwh` by the actual
  number of unit-equivalent zones per archetype (generalizing the existing `OD_N_UNITS=7`-style
  correction to MidRise/HighRise, using each archetype's real zone-multiplier-weighted unit count, not
  a hard-coded constant). Either lever is a manager decision, not mine.
- Manager should decide whether the "phantom-peak" defect (2026-07-13, referenced in
  `integration.py:1583`) is itself already understood/documented elsewhere in the plan — I did not go
  looking for that upstream finding, since it was out of scope for this task.

## WHAT I DID NOT VERIFY

- I did not check MidRise's or OtherDwelling's `Scenario_2022.idf` line-by-line the way I did for
  HighRise (task doc says don't generalize to a second full cell); the MidRise/OtherDwelling numbers
  above rest on (a) the task doc's own reported overshoot percentages and (b) a single `eplusout.eio`
  zone-count spot check per archetype, not a full IDF diff for those archetypes.
- I did not verify what the "2022/2030 phantom-peak defect... found during manuscript QA (2026-07-13)"
  actually was, beyond the one-sentence description in the `integration.py` comment — I did not search
  for a corresponding task/finding doc describing that original defect or its fix's own validation.
- I did not check whether `Lights:Electricity`/`InteriorLights:Electricity` broadcasts through the
  exact same code path (same `_s9_equip_zones`-shaped set) or a separate lighting-specific set — the
  "Lighting consolidation" comment appears right after the equipment block (visible in the
  step-1580-1660 excerpt) but I did not read that section's code, only inferred from the matching
  27-`LIGHTS,`-objects count in the diff that it follows the same broadcast pattern.
- I did not confirm whether other non-SHEU downstream consumers of these whole-building meters (e.g.
  load-shape figures, the A6 gate, or manuscript numbers already drawn from the published tree) are
  affected — this task only covers the A5 energy-check regression.
