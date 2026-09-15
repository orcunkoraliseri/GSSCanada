# Scoping note: running the Madrid stock-scale end-use campaign

Read-only investigation, 2026-09-14. All claims below carry a `path:line` the author (this note's
writer) opened directly. Where a number could not be pinned down it is marked NOT FOUND with where
was looked. Root: `4J_docs_occ/`.

---

## 1. What the campaign actually is

Step 11 (`Step11_docs/4thJ_11_stockEndUseLoads.md`) re-runs Step 9's activity-to-load trigger and
mapping — unchanged — on Step 10's real building-stock population, so the stock-scale appliance and
DHW claim Step 9 could only declare gets tested at the scale the source load models (CREST, Widen,
LPG, RAMP) were validated at (`Step11_docs/4thJ_11_stockEndUseLoads.md:90-96`).

**Inputs.** Step 10 campaign `C2` ("no-core") supplies, per city: a drawn-flat population under the
no-core dwelling-subdivision rule (`N_u := k x storeys`, `Step10_docs/4thJ_10_nocoreRealStock.md:68-71`),
one EnergyPlus cell per building per `(case, f)` combination (`case` in {A, B}, `f` in
{0, .15, .30, .50, 1.00}, ten combinations per building — confirmed shape at
`Prompts/RESUME.md:5108-5109`), and one Step-7 occupancy diary bound to each drawn flat
(`Step10_docs/4thJ_10_nocoreRealStock.md:93` "one series per drawn flat"). Step 11 never touches
EnergyPlus (`Step11_docs/4thJ_11_stockEndUseLoads.md:339` "No Speed job and no GPU").

**Tools (by path), all under `Step11_docs/`'s implied `tools/` tree, named in the work-item table:**
- `tools/4thJ_step11_trigger_campaign.py` — work item 11.3, runs the Step 9 trigger per drawn flat's
  own diary (`Step11_docs/4thJ_11_stockEndUseLoads.md:333`).
- `tools/4thJ_step11_aggregate.py` — work item 11.5, imports 11.3's trigger loop and `G9.12`'s own
  scorer, sums each flat's electricity/DHW series into one stock diurnal profile
  (`Step11_docs/4thJ_11_stockEndUseLoads.md:334`).
- `tools/4thJ_step11_stockboard.py` — work item 11.6, feeds the gate board (`G11.6`/`G11.8`/`G11.18`)
  at full population (`Step11_docs/4thJ_11_stockEndUseLoads.md:335`).

**Per-cell / per-flat runtime, London and Bologna, recorded three separate times, all agreeing at
~0.20 s/flat, single machine, no parallel workers mentioned:**
- 11.3 (trigger): Bologna 29,902 flats / 1,126 buildings in 6,126.2 s (0.2049 s/flat); London 7,602
  flats / 1,200 buildings in 1,537.3 s (0.2022 s/flat) — `Step11_docs/4thJ_11_stockEndUseLoads.md:333`.
- 11.5 (aggregation): Bologna 29,902 flats / 1,126 buildings in 5,969.9 s (0.1997 s/flat); London
  7,602 flats / 1,200 buildings in 1,567.3 s (0.2062 s/flat) — `Prompts/RESUME.md:684-685`.

**Outputs.** JSON manifests per city, e.g. `outputs_step11/c2_it/step11_11-3_it_reseed.json` (33.8 MB,
`n_flats_enumerated == n_flats_run == 29902`) and `outputs_step11/c2_uk/step11_11-3_uk_reseed.json`
(9.0 MB) (`Step11_docs/4thJ_11_stockEndUseLoads.md:333`), each flat carrying real
`dhw_litres_year`/`elec_kwh_year`/`dhw_events_by_category` fields (`Prompts/RESUME.md:1155-1157`),
plus the stock-scale aggregate manifests from 11.5/11.6 and the scored `G11.x` gate board (14 PASS,
`G11.6` limitation, `G11.12` limitation, `G11.7` INFO permanent, `G11.4` NOT CHECKED offline —
`Step11_docs/4thJ_11_stockEndUseLoads.md:339`, the work-item-11.6 row).

## 2. Why Madrid was excluded

The literal record, verbatim, `Step11_docs/4thJ_11_stockEndUseLoads.md:333`: "Madrid (ES) was never
in scope for this campaign." No elaboration sits on that line. Tracing forward through the handoff
log gives the mechanism, and it is a scheduling/pipeline-version choice, not a data or licence gap:

- The only Step-10 `C2` (no-core) run Madrid ever had was on the Speed cluster, Linux EnergyPlus
  build, job `1315013`, completed 2026-09-09/10, 11,510/11,510 cells accounted, 840
  `ENERGYPLUS_FAILED` / 84 buildings (`Prompts/RESUME.md:4663`).
- The Speed jobs for the other two cities (`1315014` IT, `1315015` UK) were cancelled mid-run around
  2026-09-11 midday and "the repair effort moved to local runs instead
  (`_local_runs\4J_IT_local`, `4J_UK_local`)" (`Prompts/RESUME.md:1490-1494`); the same entry states
  local is "now the sole authoritative record for both cities" and that "Madrid (ES) not touched, not
  polled" (`Prompts/RESUME.md:1452,1495`).
- That local re-run carried a real driver fix (`build_idf_for_cell`, an unconditional pre-extrude 1 mm
  vertex snap fixing an interzone geometry defect that stopped cells fatally before any timestep)
  applied to London and Bologna only. The record names this explicitly: "This changes
  `build_idf_for_cell`, the SAME driver Madrid's (ES) C2 campaign already ran to completion under the
  OLD code. Madrid is untouched and not being rerun — its result stands as-is under the pre-fix code
  path. Flagging only so it's a visible, deliberate choice, not an oversight, when you're back."
  (`Prompts/RESUME.md:3129-3130`).
- Step 10's own "ONE CAMPAIGN, ONE ENGINE BUILD" rule (`Step10_docs/4thJ_10_nocoreRealStock.md:604`)
  means Madrid's Speed/Linux, pre-fix cells cannot simply be pooled with London/Bologna's local
  Windows, post-fix cells as one population without breaking that rule.
- Final closure of the London/Bologna campaign records the same fact plainly: "Madrid (ES): untouched
  throughout." (`Prompts/RESUME.md:1319`, the last+230 closure block).

**Distinguishing hard blocker from scheduling choice.** There is no data gap, no licence gap, and no
hard geometric blocker specific to Madrid under the no-core regime — Madrid's own no-core eligibility
(1,100 of 1,175 buildings, `Step10_docs/4thJ_10_nocoreRealStock.md:172`) is comparable to Bologna's
(1,036 of 1,211, same line) and its Speed run demonstrably completed to 92.7% cell-level success.
The one genuine hard-blocker-shaped item in the record is the core-era (`C1`) layout contract —
convex, courtyard-free, at least 8 m wide — which accepted only 63 of 1,183 attribute-usable Madrid
footprints (`Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md:70-72`) — but that constraint
belongs to the closed, non-reported `C1` campaign and was already loosened for `C2` (Arm F redefined
to "check-FAIL or unusable footprint -> one box per floor", no longer a bare convexity refusal,
`Step10_docs/4thJ_10_nocoreRealStock.md:82-90`). The reason Madrid sits outside Step 11's scope is
that the pipeline moved to a different compute lane (local Windows, fixed driver) for two cities and
never carried Madrid along — a deliberate, flagged, but never-decided scheduling gap.

## 3. What Madrid inputs already exist on disk

**Core-era (`C1`), closed and not reported (`Step10_docs/4thJ_10_nocoreRealStock.md:15-18`, 410
cells total across all sites, 18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2 NOT_EVALUABLE):**
- Madrid Catastro INSPIRE attribute coverage: 1,883 residential features in the study bbox, all 1,883
  carrying a year, 1,183 of 1,194 EU-02 footprints (99.1%) recovering both a year and a dwelling count
  (`Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md:58-61`).
- The convex/courtyard-free/8 m layout contract accepted only **63 of 1,183** attribute-usable Madrid
  footprints (`Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md:70-72`).
- The weather file is clean and reusable regardless of era: `es_madrid_2009_2010_y2010.epw`, 8,760
  rows, dry-bulb -5.3...37.3 C, no sentinels (`Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md:1495`).
- Whatever `es` cells were simulated under `C1` are flagged unusable outright: "`es` contributes ZERO
  to the reproducible set — every completed `es` cell in every run carries an out-of-range temperature
  warning, so the Madrid fold is currently unusable, not merely reduced"
  (`Step10_docs/archive_C1_core_era/4thJ_10_ubemRealStock.md:1227`). **`C1` Madrid data is not a
  reuse candidate at any scale.**

**No-core (`C2`), the campaign this step runs on, Madrid arm:**
- Eligible population: 1,100 of 1,175 buildings by the ruled `geometry_outcome` guard
  (`Step10_docs/4thJ_10_nocoreRealStock.md:172`).
- The actual completed run: 1,151 buildings, 11,510 planned cells, 11,510 finished, 840
  `ENERGYPLUS_FAILED` = 84 distinct buildings, `payload_set_sha256` unchanged throughout
  (`Prompts/RESUME.md:4663`), i.e. **10,670 of 11,510 cells (92.7%) completed**.
- This data is stranded on the pre-driver-fix code path and on a different platform (Speed/Linux) from
  the campaign London and Bologna were finally read from (local Windows) — see Section 2.

## 4. The known Madrid damage

`Prompts/RESUME.md:1369-1377` (the last+228 closure block) records London and Bologna's final counts
and states plainly: "Madrid (ES): untouched throughout, not part of this closure"
(`Prompts/RESUME.md:1377`). `writing/4thJ_crossStep_analysis.md:408` records the number the author
asked about: "Madrid's 840 failed cells / 84 buildings were left unrepaired by deliberate choice".

The underlying record is `Step10_docs/impl/C2_ES_failure_progress_log.csv` (85 lines = header + 84
building rows, one row per building with a shortfall, columns `building_id, n_failed_cells,
confirmed_class, signature_bucket, severe_message_counts_summary, first_documented_in, notes`).
Tallied directly from that file: 84 rows, 840 non-completing cells total (`ENERGYPLUS_FAILED`, 10 per
building, matching the 10-cell-per-building shape), `confirmed_class` distribution:

| class | buildings | mechanism |
|---|---|---|
| (a) | 9 | `CalcCoordinateTransformation` route — coincident/collinear vertices deleted, degenerate surfaces, "Invalid dot product" fatal |
| (b1) | 9 | vertex-mismatch-only, byte-identical vertex rings reordered on a 1 mm grid, engine reads one vertex differently |
| (b2) | 1 | same family as (b1), not separately described in the CSV notes read |
| (c)-PURE | 4 | a third signature family present in the log, root cause not re-derived from this file alone |
| (c)-MIXED | 1 | mixture of the (c) and another signature |
| (d) | 1 | root-caused upstream `geomeppy` adjacency bug (`openubem/idf/surfaces.py:927`, `:144/169-201`) — a same-floor sliver-fragment misattribution; NOT fixed, third-party code, exposure measured at ~22% of the whole building stock (790/3,625, all three districts) but not confirmed on any other building |
| **blank** | **59** | unclassified — the CSV's own notes mark most of these "Sixth signature family, NOT merged into (d) or any class... Hypothesis only, NOT established" (zero-area and/or non-planar `CheckConvexity` severes) |

So **25 of 84 buildings (30%) have an established root cause; 59 of 84 (70%) were logged but never
diagnosed to a confirmed class** — the CSV's own language is "hypothesis only, NOT established" for
the bulk of the zero-area/non-planar family. This is a materially larger undiagnosed fraction than
Bologna's residual, which closed at 3 accepted, genuinely un-simulable courtyard buildings out of
1,126 (`Prompts/RESUME.md:1371`).

## 5. Cost

**Hardware in force now:** all 4J computation is local; Speed is fetch/read-only (per the standing
project rule, repeatedly stated, e.g. `Prompts/RESUME.md:1121-1122` "all real 4J progress now lives on the
local Windows runs" and `Step11_docs/4thJ_11_stockEndUseLoads.md:339` "No Speed job and no GPU"). The
historical Madrid Speed run (31 cpu, Linux EnergyPlus build, node `salus`, job `1315013`) is therefore
not a reusable compute lane going forward, only a reusable **prior result**.

**Step 10 (EnergyPlus geometry+energy) cost, if Madrid must be re-simulated on the current driver to
match London/Bologna's provenance.** The one clean, uninterrupted local-Windows throughput
measurement on record is London's original 6,490-cell run on `TABLETOP1`, 4 EnergyPlus workers,
started 10:03:16 and finished 18:02:03/18:02:06 the same day
(`Prompts/RESUME.md:3471,3488` — ~7h59m, 813 cells/hour). A second, noisier data point (Bologna's
final 2,488-cell resumed arm, PID 32980, 19:20:57 to 21:35:06, `Prompts/RESUME.md:3151,3310` — 2h14m,
~1,113 cells/hour, inflated because a large share of that arm's cells were known-shortfall and terminate quickly)
brackets the rate at roughly **800-1,100 cells/hour on 4 local workers**. Applying that to Madrid's own
historical cell count (**11,510 cells**, 1,151 buildings x up to 10 `(case, f)` cells,
`Prompts/RESUME.md:4663`, `:5108-5109`) gives **roughly 10.5-14.5 hours of local EnergyPlus wall time**
for a from-scratch Madrid re-run on the current driver — call it **about 11-15 hours, one working day
on a single local machine**.

**Step 11 (Python trigger + aggregation) cost.** At the measured ~0.20 s/flat rate (Section 1), each
of the three passes (11.3 trigger, 11.5 aggregation, 11.6 stockboard) over a Madrid flat population of
the same order as Bologna's (Madrid's eligible-building count, 1,100 of 1,175, is close to Bologna's
1,036 of 1,211 — `Step10_docs/4thJ_10_nocoreRealStock.md:172` — so a Bologna-like density, ~25,000-
30,000 flats, is the best available proxy; NOT FOUND: no confirmed Madrid flat-count under the final
no-core `N_u` re-derivation, only the raw Arm D entry/zone counts at
`Step10_docs/4thJ_10_nocoreRealStock.md:549`, es 1,100 buildings / 11,244 raw zone entries, which
undercounts the final drawn-flat population by the same widening London and Bologna both saw) would
run roughly 1.4-1.7 hours; three passes, roughly **4-5 hours** total, single machine, no GPU.

**Total estimate for a from-scratch Madrid campaign matching London/Bologna's current provenance:
roughly 15-20 hours of local, single-machine wall time (EnergyPlus + Step 11 Python), on the order of
one to two working days**, before allowing for the memory-watchdog interruptions this same local
pipeline has repeatedly hit on IT/UK (`Prompts/RESUME.md:1296` "week's well-documented pattern of
memory-watchdog kills on this box").

## 6. The shortest honest path

Ranked cheapest to most expensive:

1. **Reuse the existing Speed-era Madrid cells as-is (zero compute).** Lets the paper report a Madrid
   population and cell-level success rate (10,670/11,510, 92.7%) as a footnoted, separate-provenance
   number. Does **not** let the paper pool Madrid with London/Bologna in one stock-scale statistic —
   it sits on a different engine build and a pre-driver-fix code path
   (`Prompts/RESUME.md:3129-3130`, `Step10_docs/4thJ_10_nocoreRealStock.md:604`), and 70% of its
   shortfall buildings (Section 4) carry no confirmed root cause, which is a materially weaker limitation
   record than the other two cities'.

2. **Re-run only the 840 non-completing cells (84 buildings) under the current fixed driver, local Windows,
   ~1-2 hours EnergyPlus.** Cheapest real repair. Would raise Madrid's completed-cell count and let
   the paper state a smaller, better-diagnosed shortfall. It does **not** by itself establish
   provenance parity with London/Bologna: the driver fix's vertex snap runs unconditionally on every
   zone, not only the ones with a shortfall (`Prompts/RESUME.md:3115`), so the other 10,670 already-completed
   Madrid cells were never independently re-verified against the fixed geometry path. This option lets
   the paper claim a repaired Madrid shortfall, but not a verified full-population match to the current
   pipeline version.

3. **Run the full Madrid no-core stock campaign from scratch on the current driver, local Windows,
   matching London/Bologna's exact provenance — roughly 11-15 hours EnergyPlus + 4-5 hours Step 11,
   about 15-20 hours total (Section 5).** The only option that gives the paper a Madrid population on
   the same engine build, driver code, and Step 11 processing chain as London and Bologna, and so the
   only option that lets the paper make the full three-country pooled or directly-compared appliance-
   peak claim without a provenance caveat.
