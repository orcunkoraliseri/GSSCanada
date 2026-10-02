# 4J — re-run London and Bologna stock-scale end use after the OpenUBEM neighbourhood fix (plan, 2026-10-01)

Status: **PLAN, nothing run yet.** Handoff: `Prompts/RESUME.md` last+308. Board: artifact SJX4RXb7CneNRARitNnHez.
OpenUBEM's answer: `OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/2026-10-01_OpenUBEM_to_4J_neighbourhood_setup_what_to_repeat.md`
(it contains London content; never forward it to the 5J session).

## 0. What the author decided (2026-10-01)

- **Drop** the observed-stock heating campaign (C2, 35,090 cells) and the 410-cell exploratory layout run from
  the paper and the SI.
- **Re-run only** the stock-scale appliance and hot-water loads for **London and Bologna**.
- Submission to Energy and Buildings stays on hold until this plan is closed.

## 1. Why the runs must be repeated

OpenUBEM found four defects in the neighbourhood models. Three are fixed in `EU-11/<D>_win_2026-10-03`:
walls facing inward, no windows, and overlapping or wrongly bounded flats. The fourth is **not fixed yet**:
London and Bologna have no observed flat counts, so every block of flats got the TABULA reference count
(78 or 40 flats) whatever its size. The new rule (owner, 2026-10-01): the flat count follows the floor area.

Appliance and hot-water loads are summed per flat. So the flat count is the one defect that changes our
numbers. Walls, windows and weather do not affect these loads.

## 2. Why we cannot run today (answer to the author's question)

- The `_win_2026-10-03` models are ready, but they still carry the **old flat counts**, the exact defect we
  need fixed. Running on them would reproduce 7,602 and 29,902 flats.
- The corrected counts come in `<D>_win_2026-10-04`. Checked on disk 2026-10-01: that folder does not exist
  yet, and the layout files we read (`OpenUBEM/openubem/outputs/3D/eu_<D>_data/layouts/`) are still from 09-09.
- OpenUBEM's earliest date is 2026-10-02, after their own check.
- **What we can do now:** build and test every tool on the `_win_2026-10-03` models (Phase 1), so the real
  run starts the hour the new counts land.

## 3. How the old numbers were made (traced from disk 2026-10-01)

| Stage | Tool | Input | Output |
|---|---|---|---|
| Flats + one diary per flat | `tools/4thJ_step10_nocore_campaign.py` (C2, EnergyPlus 23.1, 2 cases x 5 gain levels = 10 cells per building) | OpenUBEM layouts `outputs/3D/eu_<D>_data/layouts/*.json` | `_local_runs/4J_{UK,IT}_local/out/<D>/cells/` (London 12,070, Bologna 11,681 files) |
| Filter | copy of cells without the 49 floor-averaged buildings | the cells above | `_local_runs/4J_{UK,IT}_local/out/<D>_step11input/` |
| Trigger (11.3) | `tools/4thJ_step11_trigger_campaign.py --diary-diversity reseed` | `--c2-out` = the filtered copy | `Step11_docs/outputs_step11/c2_{uk,it}/step11_11-3_*_reseed.json` |
| Aggregate (11.5, R² vs UK reference) | `tools/4thJ_step11_aggregate.py` | same | `.../c2_{uk,it}/step11_11-5_*_reseed.json` (R² 0.4347 / 0.0781) |
| Stockboard (G11.6/8/18, hot water) | `tools/4thJ_step11_stockboard.py` | same | `.../g11_6_18/c2_{uk,it}/` (202.41 / 200.35 L) |
| Gates | `tools/4thJ_gates_step11.py`, `tools/4thJ_step11_selftest.py` | the outputs above | `.../g11_6_18/gates_step11_full.json`, `selftest_full.json` |

🔴 **Key dependency:** the Step 11 tools read their flat list and diaries **from the C2 heating cells**
(`flats_from_cells`, `read_c2_cells`; refusal S3 if no cells, S4 if a cell did not complete). The heating
results are never used, only the flat list and the diary bound to each flat. So dropping C2 from the paper
does not remove it as an input. Decision D1 settles this.

## 3b. 🔴 Second defect, in OUR Step 11 runs (found 2026-10-01 during the dry run)

Every C2 building is simulated twice: **Case A** (one diary copied to every flat) and **Case B** (an own diary per
flat; `tools/4thJ_step10_paired.py:5-6`). `flats_from_cells` keys flats by (building, **case**, unit)
(`tools/4thJ_step11_trigger_campaign.py:304`) and `4thJ_step11_aggregate.py` sums every flat, so **each real flat
was counted twice**, once with a copied diary. The London dry run registers 3,910 dwellings; 3,801 after the
excluded buildings, and 2 x 3,801 = 7,602, the paper's "flats". Bologna 29,902 = 2 x 14,951. The Step 11 design
always meant Case B only (`4thJ_11_stockEndUseLoads.md`, "Bologna Case B alone is ~9 h").
**Fix, no tool change:** the `<D>_step11input` copy keeps **Case B cells only** (as the 49-building filter was
done). New check: flats in Step 11 = dwellings registered by C2 minus excluded buildings' dwellings, exactly.

## 4. Decisions for the author

**D1. How do we get the new flat list?** (needed before Phase 2)
- **Option A, recommended: re-run C2 for London and Bologna only, as an input step.** Unchanged code, so no
  new defects in the flat and diary logic. Cost: about 1,200 x 10 London cells and 1,126 x 10 Bologna
  cells on EnergyPlus 23.1 (the earlier local runs took about half a day per city). Heating output is not
  reported anywhere.
- **Option B: a new reader that takes the flat list straight from the OpenUBEM models**, with no EnergyPlus.
  Faster to run, but new code: diary assignment must be shown identical to C2's (seed rule, reseed), and a
  new check is needed that the flat total matches OpenUBEM's own count.
- My advice: A. B saves compute but adds the riskiest kind of change (new code just before submission).

**D2. Re-pin rule.** New layouts change the payload digest, and maybe the OpenUBEM engine digest
(`ENGINE_DIGEST_PIN`, `tools/4thJ_step10_nocore_preflight.py:104`). House rule: a pin is never moved to make
a run pass. The author confirms in one sentence that the move is for the OpenUBEM fix, and the old and new
digests are recorded beside each other.

## 5. Task list

### Phase 0 — Records (DONE 2026-10-01)
- [x] OpenUBEM asked; answer on disk (see top).
- [x] RESUME last+308, memory, board (log line + sims row), AUTHOR_TODO item 0.
- [x] Author: drop C2 + 410-cell run; re-run London + Bologna only.
- [x] This plan read by the author; D1 and D2 answered (2026-10-01): **D1 = option A** (re-run C2 London + Bologna
      as an input step, unchanged code). **D2 = re-pin allowed; record and present only the NEW values** (old values
      are wrong, so no before/after tables anywhere).

### Phase 1 — Prepare now, on the `_win_2026-10-03` models (no waiting)
- [x] 1.1 (DONE 2026-10-01, sizes equal after the move) Back up the old outputs: move `Step11_docs/outputs_step11/c2_{uk,it}` and `g11_6_18` to
      `Step11_docs/outputs_step11/previous/pre_neighbourhood_fix_20261001/`, and the `_local_runs/4J_{UK,IT}_local`
      trees to `_local_runs/previous/`. Check the sizes match before anything is deleted (nothing is deleted).
- [-] 1.2 DROPPED (author, D2): old numbers are wrong and are not tabulated or presented.
- [x] 1.3 (DONE 2026-10-01; answer: 10-04 earliest 2 Oct; side-cars regenerated with new counts after their
      audit, no date; per-building CSV building_id/old_count/new_count will come; they send per-file sha256 at the
      freeze; no public interface change so far) Ask OpenUBEM for: (a) the 10-04 paths and digests; (b) a per-building table with the new flat
      count; (c) whether layout side-cars for 10-04 will exist and when; (d) the new engine digest.
- [x] 1.4 (DONE 2026-10-01) Pins refuse as expected (engine and no-core files both changed). With the pins
      overridden IN MEMORY ONLY (`scratchpad/dry/smoke_wrap.py`, never for a real run), London `--dry-run
      --limit 2` passes preflight on today's code + 09-09 layouts: 1,207 eligible buildings, 12,070 cells,
      3,910 dwellings. No interface break. This is what found defect 3b.
- [ ] 1.4b Where to run: locally, as the earlier London and Bologna runs were (OpenUBEM code and layouts live
      here; no copy to Speed to keep in sync), 4 EnergyPlus workers + memory watchdog. Option A of the C2 runner (`--dry-run`) on London and Bologna against the current layouts,
      to see which pins and refusals fire. Fix only what the OpenUBEM change requires; every patch prints
      its own line.
- [-] 1.5 NOT CHOSEN. Option B: write the reader, then a 200-flat smoke on 10-03 data, compared with the
      old Step 11 output for the same buildings (same diaries, same totals).
- [x] 1.6 (DONE 2026-10-01: `_local_runs/4J_rerun_20261001/run_rerun.ps1` + `watchdog.ps1`; 10 workers = half of
      the 20 local CPUs (author), minus 2 after each memory-guard stop; parses clean; smoke stops at the pin
      refusal with exit 1, as it must; new tool `tools/4thJ_step11_make_input.py` tested: 3,801 London flats PASS,
      planted Case A cell FAIL, wrong OpenUBEM count FAIL) Write the local launch script for each stage (C2 with `--resume`, filter, 11.3, 11.5, stockboard,
      gates), with the memory watchdog; syntax check plus a 1-building smoke.
- [x] 1.7 (DONE 2026-10-01: `IMP/docs/2026-10-01_rerun_text_drafts.md`) Draft the manuscript and SI text changes with placeholders `[N_LDN]`, `[N_BOL]`, `[R2_LDN]` etc.
      (Phase 4 list), so only numbers are filled in later.

### Phase 2 — When the 10-05 models arrive (was 10-04; see log 2026-10-01 late)
- [ ] 2.1 Read OpenUBEM's audit note. Check digests against what they sent.
- [ ] 2.2 Count check: our flat total per district = OpenUBEM's flat total. Must match exactly; a mismatch
      stops the run.
- [ ] 2.3 Planted fault: drop one building from the input and confirm 2.2 fails (gate seen failing).
- [ ] 2.4 Re-pin (D2): write the NEW digests, with the author's 2026-10-01 approval quoted beside them.
- [ ] 2.5 Smoke: 1 London and 1 Bologna building end to end.

### Phase 3 — Runs (local, as the earlier London and Bologna runs)
- [ ] 3.1 Flats + diaries (Option A: C2 London + Bologna; Option B: the reader). Check: every building
      planned = finished, failed list read by name.
- [ ] 3.2 Build `<D>_step11input`: **Case B cells only** (3b) and without floor-averaged buildings; record the
      excluded count. Check: Step 11 flats = C2 dwellings registered minus excluded dwellings. Planted fault:
      add one Case A cell and confirm the check fails.
- [ ] 3.3 Trigger 11.3, `--diary-diversity reseed`, both cities.
- [ ] 3.4 Aggregate 11.5, both cities (new R²).
- [ ] 3.5 Stockboard G11.6/8/18, both cities (new litres per dwelling-day).
- [ ] 3.6 Gates + 16-mutation self-test; must still print `COVERAGE CLAUSE: PASS`.
- [ ] 3.7 Board sims row updated after each stage (per-job progress).

### Phase 4 — Results
- [ ] 4.1 One results table with the NEW values only (flats, buildings, excluded, R², litres, G11.x verdicts).
- [ ] 4.2 Check the text's claims against the new values: R² below the 0.85 floor? hot water inside 200 ± 10%?
      If a claim no longer holds, stop and tell the author before touching the text.
- [ ] 4.3 Write the closure note in `Step11_docs/docs/` with the evidence paths.

### Phase 5 — Manuscript (`writing/submission/4J_manuscript_submission.md`, backup first)
- [ ] 5.1 Line 69 (Table, "Observed building stock" row): keep London and Bologna; check wording.
- [ ] 5.2 Line 129: new flat and building counts; new excluded-building count; replace "A heating campaign on
      observed stock ... Supplementary S9; no result from it is used here." (C2 dropped).
- [ ] 5.3 Line 237: new stock-scale R² for London and Bologna; re-read the laundry-cause sentence still holds.
- [ ] 5.4 Grep for every other stock number and for "observed stock", "35,090", "410", "C2", "Madrid"
      (Madrid now appears nowhere in stock results). Lines 299 and 303 mention the heating and reproduction
      limits: check they do not lean on C2.
- [ ] 5.5 Say how flat counts are set: "follows floor area" (the old SI text says counts come from national
      registries, which was never true for London and Bologna).
- [ ] 5.6 Abstract, highlights, Conclusion: check no stock number or C2 claim sits there.
- [ ] 5.7 Word count (prose ≤ ~7,500 with `wc_prose.py`).

### Phase 6 — Supplementary material (`4J_supplementary_material.md`, backup first)
- [ ] 6.1 Line 9 contents paragraph: S9 renamed (e.g. "S9 the stock-scale end-use run").
- [ ] 6.2 Lines 191-193 (runs table): delete the C2 and 410-cell rows; update the stock-scale row.
- [ ] 6.3 Lines 386 and 397-399: new R² and litres.
- [ ] 6.4 Lines 424-428 (exploratory layout paragraph in S7.6): delete.
- [ ] 6.5 Lines 457-476 (S9): delete the heating campaign and exploratory layout paragraphs; rewrite the
      stock-scale paragraph (new counts, flat counts follow floor area, new excluded count).
- [ ] 6.6 Lines 566, 584, 599, 620: remove or rewrite every C2 mention (sensitivity design, reproducibility,
      "no scored result from the larger campaign", limitations).
- [ ] 6.7 Grep the whole SI for "observed-stock", "C2", "35,090", "410", "Madrid", "courtyard"; each hit kept
      only if it is not about the dropped runs.
- [ ] 6.8 Section and table cross-references still resolve (S-numbers, Table S-numbers).

### Phase 7 — Figures, tables, graphical abstract
- [x] 7.1 (DONE: Figure 6 reads `Step9_docs/outputs_step9_P3`) Figure 6 and Table S4 use the 100-dwelling Step 9 runs, not the stock runs: confirm, no change expected.
- [x] 7.2 (DONE: installed Figure 1 box reads "Stock-scale loads: London and Bologna"; still true, no change) Figure 1 (workflow) and `generate_fig01_pipeline.py` cards 10-11 ("Real-stock UBEM", "observed
      footprints, one diary per dwelling"): card 10 describes C2. Decide with the author: reword to "stock
      flats and diaries" or drop. Figure 1 is author-drawn (Gemini): write the change prompt, never the image.
- [x] 7.3 (DONE: `generate_graphical_abstract.py` has no stock or district text) Graphical abstract: check for any stock or district content.
- [x] 7.4 (DONE: Figure 7 values are Table 10, archetype campaign, three countries) Figure 7 (heating null): confirm it uses the archetype runs, not C2.
- [ ] 7.5 Any figure that changes: redraw from data, check labels for clashes, export PDF + PNG.

### Phase 8 — Build and upload
- [ ] 8.1 Rebuild manuscript and SI docx with the usual scripts (both PATCH lines printed).
- [ ] 8.2 Number check: every number in 5.x and 6.x re-read from the output JSON, not from this plan.
- [ ] 8.3 Copy to `EB_upload/`, old copy to `previous/EB_upload_pre_20261001/`; record md5.
- [ ] 8.4 Cover letter: no change expected (check it does not mention C2 or district counts).

### Phase 9 — Close
- [ ] 9.1 RESUME, memory, board (log line + sims row done), AUTHOR_TODO.
- [ ] 9.2 Tell OpenUBEM which digests 4J used.
- [ ] 9.3 Author: cover-letter date, final read, submit.

## 6. Risks to watch

- A verdict that flips after the re-run (4.2): stop and ask, never reword around it.
- New counts could make Bologna much smaller than 29,902 flats; the "1,200 to 30,000 flats" scale argument
  in the text may need a softer claim.
- Pins (D2) refusing the run: never move a pin silently.
- Old outputs mixed with new ones: Phase 1.1 moves them away first, and the run counts must drop to zero
  before the new run starts.

## 7. Progress log
- 2026-10-01: Phase 0, Phase 1 (except 1.5, not chosen) and Phase 7.1-7.4 DONE. Everything left waits for OpenUBEM's
  `_win_2026-10-05` models, the regenerated layout side-cars and the per-building count CSV.
  When they arrive: put the new engine and no-core sha256 into `tools/4thJ_step10_nocore_preflight.py` (ENGINE_DIGEST_PIN,
  NOCORE_DIGEST_PIN; comment = author approval 2026-10-01, new values only), then
  `powershell -NoProfile -File C:\Users\o_iseri\Desktop\GSSCanada\_local_runs\4J_rerun_20261001\run_rerun.ps1 -Smoke ...`,
  then the full run with `-LdnCounts <csv> -BolCounts <csv>`.
- 2026-10-01 (later): asked OpenUBEM for per-building flat counts. Reply
  (`OpenUBEM/docs/docs_ACTIVE/europeanLocations/messages_GSSCanada/2026-10-01_OpenUBEM_to_4J_flat_counts_status.md`, London content,
  never to 5J): NOT READY, do not start. London 10-04 counts exist but are unaudited, and the zero-area surface fix is still going in.
  Bologna 10-04 is still being built. 10-03 holds the OLD counts, so never use it. Side-cars not regenerated. Everything comes together
  after their audit, not before 2 Oct. Rule confirmed (their `scripts/run_eu_s2_district_campaign.py:149-168`): SFH/TH = 1;
  observed count wins (Madrid only); else max(1, round(footprint x storeys / (a_c_ref / n_apartment))), Python round-half-even;
  missing inputs -> reference n_apartment. SI-6 draft updated to this rule. CSV columns: building_id,old_count,new_count,
  dwellings_source,status. building_id = side-car path (`relation/6171462`), same form as our cells (`way/1054785382`), so
  CHECK 2 matches directly; it compares the runner's emitted flats with new_count and never re-computes the rule, so halves cannot trip it.
- 2026-10-01 (late): OpenUBEM peer message: use the **10-05** models, not 10-04 (never 10-03/10-04). London `GB-LDN-STDUNSTANS_win_2026-10-05`
  (counts same as 10-04: 196 buildings changed, 6,127 -> 6,465 flats). Bologna `IT-BOL-GALVANI2_win_2026-10-05` (1,070 of 1,179 changed,
  15,767 -> 36,095 flats, none < 15 m2, max building 30090 = 1,247 flats). Bologna IDFs now local origin (dx 685000, dy 4928000, EPSG:32632;
  x/y shift only); side-cars return in map coordinates. Both passed their audit, running on their cluster. Count CSVs (+ sha256, module sha256):
  London not before the afternoon of 2 Oct, Bologna not before the morning of 3 Oct. Rule unchanged. Action: when they arrive, pin 10-05
  paths + digests (Phase 2); nothing started. Read every "10-04" above as 10-05.
